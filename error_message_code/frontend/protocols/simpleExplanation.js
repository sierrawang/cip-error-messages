// Simple error messages are taken from https://github.com/Tobias-Kohn/TigerPython-Parser/

import { TPyParser } from './tigerpython-parser.js';
import { getStandardError, getTrimError, yellowText } from '../errorhint.js';

export function getTigerPythonErrorHelper(code) {
    const allSyntaxErrors = TPyParser.findAllErrors(code);

    // Get the syntax error, but ignore the f string error message
    for (let i = 0; i < allSyntaxErrors.length; i++) {
        const err = allSyntaxErrors[i];
        if (err.msg !== "This is an invalid string prefix: 'f'.") {
            return err;
        }
    }

    return null;
}

// Outputs TigerPython enhanced syntax error messages and trimmed compiler error messages
export function getTigerPythonError(code, stderr, term) {
    const err = getTigerPythonErrorHelper(code);
    if (err) {
        return getTrimError(code, stderr) + "\r\n" + yellowText(err.msg);
    } 
    
    return getStandardError(code, stderr);
}