import * as dotenv from 'dotenv';
dotenv.config();

import readlineSync from 'readline-sync';
import { GoogleGenerativeAIEmbeddings } from '@langchain/google-genai';
import { Pinecone } from '@pinecone-database/pinecone';
import { GoogleGenAI } from "@google/genai";

const History = [];
const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

/**
 * Rewrites a follow-up question into a standalone query.
 */
async function transformQuery(question) {
    // Temporarily add question to history for context
    History.push({
        role: 'user',
        parts: [{ text: question }]
    });

    const response = await ai.models.generateContent({
        model: "gemini-2.0-flash",
        contents: History,
        config: {
            systemInstruction: `You are a query rewriting expert. Based on the provided chat history, 
            rephrase the "Follow Up user Question" into a complete, standalone question 
            that can be understood without the chat history.
            Only output the rewritten question and nothing else.`,
        },
    });

    // Remove the temporary addition
    History.pop();

    // Extract the rewritten question
    if (response.candidates?.length > 0) {
        const parts = response.candidates[0].content?.parts;
        if (parts?.length > 0 && parts[0].text) {
            return parts[0].text.trim();
        }
    }
    return question; // fallback if rewrite fails
}

/**
 * Handles the main Q&A process
 */
async function chatting(userProblem) {
    const rewrittenQuery = await transformQuery(userProblem);

    // Step 1: Generate embeddings for the rewritten query
    const embeddings = new GoogleGenerativeAIEmbeddings({
        apiKey: process.env.GEMINI_API_KEY,
        model: 'text-embedding-004',
    });

    const queryVector = await embeddings.embedQuery(rewrittenQuery);

    // Step 2: Search in Pinecone
    const pinecone = new Pinecone({ apiKey: process.env.PINECONE_API_KEY });
    const pineconeIndex = pinecone.Index(process.env.PINECONE_INDEX_NAME);

    const searchResults = await pineconeIndex.query({
        topK: 10,
        vector: queryVector,
        includeMetadata: true,
    });

    const context = searchResults.matches
        .map(match => match.metadata.text)
        .join("\n\n---\n\n");

    // Step 3: Add user question to history
    History.push({
        role: 'user',
        parts: [{ text: userProblem }]
    });

    // Step 4: Call Gemini API for answer
    const response = await ai.models.generateContent({
        model: "gemini-2.0-flash",
        contents: History,
        config: {
            systemInstruction: `You have to behave like a Resume Data Analyst Expert.
            You will be given a context of relevant information and a user question.
            Your task is to answer the user's question based ONLY on the provided context.
            If the answer is not in the context, you must say "I could not find the answer in the provided document."
            Keep your answers clear, concise, and educational.
              
            Context: ${context}
            `,
        },
    });

    // Step 5: Extract model's reply safely
    let modelReply = "";
    if (response.candidates?.length > 0) {
        const parts = response.candidates[0].content?.parts;
        if (parts?.length > 0 && parts[0].text) {
            modelReply = parts[0].text.trim();
        }
    }

    // Step 6: Add model reply to history
    History.push({
        role: 'model',
        parts: [{ text: modelReply }]
    });

    // Step 7: Print the reply
    console.log("\n" + modelReply + "\n");
}

/**
 * Starts interactive chat loop
 */
async function main() {
    while (true) {
        const userProblem = readlineSync.question("Ask me anything --> ");
        await chatting(userProblem);
    }
}

main();

