import { callGPT3Completion } from "utils/gpt";
import { getLastLineOfError, getTrimError, yellowText } from "../errorhint";

export async function getGPTShortExplanation(stderr, term) {
    term.writeAndScroll("\r\n" + yellowText("The AI is thinking..."))
    const errorMsg = getLastLineOfError(stderr);
    const prompt = "I ran my Python code and recieved this error: " + errorMsg +
        "In one sentence, this happened because ";
    const response = await callGPT3Completion(prompt, 200, "text-davinci-003")
    const trimmedResponse = "This happened because " + ("" + response).trim()
    return trimmedResponse
}

export async function getGPTLongExplanation(stderr, term) {
    term.writeAndScroll("\r\n" + yellowText("The AI is thinking..."))
    const errorMsg = getLastLineOfError(stderr);
    const prompt = "I ran my Python code and recieved this error: " + errorMsg +
        "This happened because ";
    const response = await callGPT3Completion(prompt, 1000, "text-davinci-003")
    const trimmedResponse = "This happened because " + ("" + response).trim()
    return trimmedResponse
}

export async function getGPTCodeExplanation(code, stderr, term) {
    term.writeAndScroll("\r\n" +
        yellowText(`Your code had an error so we are getting a message from a service called GPT. ` +
            `It might take a second, thank you for being patient!\r\n`))

    const prompt = "Python code: \n" + code +
        "\nError message: \n" + getLastLineOfError(stderr) +
        "\nText explanation of all the most likely reasons that could have caused this error: \n"

    const gptResponse = await callGPT3Completion(prompt, 1000, "text-davinci-003", 0.1);

    // Add the gpt explanation
    const trimmedErr = getTrimError(code, stderr);
    return trimmedErr + "\r\n" + yellowText(("" + gptResponse).trim());
}