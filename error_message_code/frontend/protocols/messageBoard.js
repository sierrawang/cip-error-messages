// Message board error messages was inspired by https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8870155
// Default keys came from https://github.com/cemc/cscircles-wp-content/blob/master/plugins/pybox/plugin-errorhint-en_US.php

import { getTrimError, getLastLineOfError, yellowText } from "../errorhint";

const foundPostMsg = `\r\nIt looks like there is a forum post for this error, check it out!\r\n${window.location.origin}/cip3/forum?post=`;
const suggestPostMsg = `\r\nUnfortunately, there is not a forum post for this error, why don't you make one!\r\n${window.location.origin}/cip3/forum`;

export function getMessageBoardError(code, stderr, links) {
    // Get the trimmed error message
    const trimmedErr = getTrimError(code, stderr);

    // Grab the last line of the stderr
    const error = getLastLineOfError(stderr);

    if (links) {
        for (let doc of links.docs) {
            // Each doc id is a regex for a common error message
            const regx = new RegExp(doc.id)
            if (regx.test(error)) {
                const postIds = doc.data().postIds
                if (postIds.length > 0) {
                    // Randomly choose one of the posts to return
                    const randomIndex = Math.floor(Math.random() * postIds.length);
                    return trimmedErr + yellowText(foundPostMsg + postIds[randomIndex]);
                }
                break;
            }
        }
    }

    return trimmedErr + yellowText(suggestPostMsg);
}