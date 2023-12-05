import { yellowText } from "../errorhint";
import { getTrimError } from "../errorhint";

// Outputs a readable explanation for the most common python error messages
const lineWithNumber = /Line (\d+):/;
export function getKarelError(code, stderr) {
  if (lineWithNumber.test(stderr)) {
    // This is a karel error
    const result = stderr.replace(/Line (\d+)/g, (match, lineNumber) => {
      const nextLineNumber = parseInt(lineNumber) + 1;
      return `Line ${nextLineNumber}`;
    });
    return yellowText(result)
  } else {
    // This is a pyodide error
    return getTrimError(code, stderr)
  }
}
