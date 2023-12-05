import { callGPT3Completion } from "utils/gpt";
import { getLastLineOfError, getTrimError, yellowText } from "../errorhint";


export async function getSuperheroError(code, stderr, term) {
    term.writeAndScroll("\r\n" +
        yellowText(`It looks like you have an error, one minute while we ask a superhero what is going on...\r\n`))

    const prompt = "Python code: \n" + code +
        "\nError message: \n" + getLastLineOfError(stderr) +
        "\nSuperhero text explanation of all the most likely reasons that could have caused this error (in a superhero's voice): \n"

    const gptResponse = await callGPT3Completion(prompt, 1000, "text-davinci-003", 0.1);

    // Add the gpt explanation
    const trimmedErr = getTrimError(code, stderr);
    return trimmedErr + "\r\n" + yellowText(("" + gptResponse).trim());
}