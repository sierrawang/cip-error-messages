// This file contains Sierra's implementations for more helpful error messages
// to be used and tested in Code in Place 2023. These error message types were
// inspired/copied from others' work. The goal of this work is to compare the
// different enhancement techniques.

import { getMessageBoardError } from './protocols/messageBoard.js';
import { getExplainError } from './protocols/longExplanation.js';
import { getTigerPythonError, getTigerPythonErrorHelper } from './protocols/simpleExplanation.js';
import { getKarelError } from './protocols/karelError.js';
import { getGPTCodeExplanation } from './protocols/gpt.js';
import { getSuperheroError } from './protocols/superhero.js';

export const getErrorMessage = async (code, stderr, type, term, links) => {
    console.log(type, code, stderr);
    if (term.isKarel) {
        return getKarelError(code, stderr);
    }

    switch (type) {
        case "tigerpython":
            return getTigerPythonError(code, stderr, term);
        case "explain":
            return getExplainError(code, stderr, term);
        case "messageboard":
            return getMessageBoardError(code, stderr, links);
        case "gpt":
            return await getGPTCodeExplanation(code, stderr, term);
        case "superhero":
            return await getSuperheroError(code, stderr, term);
        default:
            return getStandardError(code, stderr);
    }
}

export function yellowText(text) {
    return '\x1B[33m' + text + '\x1B[0m';
}

export function underlineText(text) {
    return '\x1B[4:1m' + text + '\x1B[0m';
}

export function boldText(text) {
    return '\x1B[1m' + text + '\x1B[0m';
}

export function normalize(error) {
    // Remove everything inside of single quotes
    error = error.replace(/ '.*'( |$)/g, " '' ");

    // Remove everything inside of double quotes
    error = error.replace(/\".*\"/g, "\"\"");

    // Replace all numbers with zero
    error = error.replace(/\\d+/g, "0");

    // Replace all function names with func()
    error = error.replace(/\\b\\w+\\(\\)/g, "func()");

    // Remove excessive details for this specific error type
    error = error.replace(/TypeError: unsupported operand type\(s\)(.*)/, "TypeError: unsupported operand type(s)")

    return error;
}

export function getLastLineOfError(stderr) {
    const errorLines = stderr.trim().split("\n");
    return errorLines[errorLines.length - 1];
}

const runtimePattern = /File "<exec>", line \d+, in mainApp/;
const syntaxPattern = /File "<exec>", line \d+/;

function formatError(stderr, pattern) {
    var oldErrorLines = stderr.trim().split("\n");

    // Add the first line to the new error message (aka Traceback (most recent call last))
    var newErrorLines = [oldErrorLines[0].trim()];

    var relevant = false;
    for (var i = 1; i < oldErrorLines.length; i++) {
        var line = oldErrorLines[i];
        if (pattern.test(line)) {
            relevant = true;
        }

        if (relevant) {
            newErrorLines.push(line.replace(/line (\d+)/g, (match, lineNumber) => `line ${parseInt(lineNumber) - 5}`));
        }
    }

    // Make the last value of the array bold and underlined
    newErrorLines[newErrorLines.length - 1] = boldText(underlineText(newErrorLines[newErrorLines.length - 1]));

    // Return the new error message
    return yellowText(newErrorLines.join("\r\n"));
}

function formatUnknownError(stderr) {
    var errorLines = stderr.trim().split("\n");
    for (var i = 0; i < errorLines.length; i++) {
        var line = errorLines[i];
        const lineText = line.split(/\s+/);
        if (lineText[0] === "") {
            lineText.shift();
        }

        errorLines[i] = lineText.join(" ");
    }
    errorLines[errorLines.length - 1] = boldText(underlineText(errorLines[errorLines.length - 1]));

    return yellowText(errorLines.join("\r\n"));
}

export function getStandardError(code, stderr) {
    if (runtimePattern.test(stderr)) {
        return formatError(stderr, runtimePattern);
    } else if (syntaxPattern.test(stderr)) {
        return formatError(stderr, syntaxPattern);
    } else {
        return formatUnknownError(stderr);
    }
}

// Get the line of stderr that contains the line number
const lineWithNumber = /File "<exec>", line (\d+)/;
export function getLineNumber(stderr) {
    const errorLines = stderr.split("\n");
    for (let i = errorLines.length - 1; i >= 0; i--) {
        const line = errorLines[i];
        const match = line.match(lineWithNumber);
        if (match) {
            const lineNumber = match[1];
            return lineNumber - 5;
        }
    }
    return -1;
}

// Outputs the line number and last line of error message
export function getTrimError(code, stderr) {
    const lineNum = getLineNumber(stderr);
    const error = getLastLineOfError(stderr);
    if (lineNum < 0) {
        return yellowText(boldText(error))
    }
    return yellowText(boldText(underlineText("(Line " + lineNum + ") " + error)));
}
