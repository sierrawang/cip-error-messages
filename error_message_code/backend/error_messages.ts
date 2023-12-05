import * as functions from "firebase-functions";
import * as admin from "firebase-admin";
import { QueryDocumentSnapshot } from "firebase-functions/v1/firestore";
import { Change, EventContext } from "firebase-functions";

// Regex for the common error messages
// Inspired by https://github.com/cemc/cscircles-wp-content/blob/master/plugins/pybox/plugin-errorhint-en_US.php
// These are the only error messages that we store forum links for
const commonErrors = [
    /NameError: (global )?name '(.*)' is not defined/,
    /SyntaxError: invalid syntax/,
    /EOFError: EOF when reading a line/,
    /TypeError: unsupported operand type\(s\) .*/,
    /SyntaxError: unexpected EOF while parsing/,
    /IndentationError: unindent does not match any outer indentation level/,
    /SyntaxError: EOL while scanning string literal/,
    /IndentationError: unexpected indent/,
    /TabError: inconsistent use of tabs and spaces in indentation/,
    /IndentationError: expected an indented block/,
    /ValueError: invalid literal for (\w+)\(\) with base \d+.*/,
    /TypeError: '(.+)' object is not iterable/,
    /TypeError: '(.+)' object is not callable/,
    /TypeError: can't multiply sequence by non-int of type '(.+)'/,
    /IndexError: (string|list) index out of range/,
    /SyntaxError: unexpected character after line continuation character/,
    /TypeError: Can't convert '(.+)' object to str implicitly/,
    /AttributeError: '(.+)' object has no attribute '(.+)'/,
    /TypeError: '(.+)' object is not subscriptable/,
    /TypeError: string indices must be integers/,
    /SyntaxError: cannot assign to (function call|literal)/,
    /UnboundLocalError: local variable '(.+)' referenced before assignment/,
    /SyntaxError: cannot assign to operator/,
    /ValueError: could not convert string to float:(.*)/,
    /TypeError: unorderable types: (.*)/,
    /TypeError: not all arguments converted during string formatting/,
    /TypeError: (object of type '.*' has no .*\(.*\)|bad operand type for .*|.* argument must be a .*)/,
    /TypeError: '.*' object cannot be interpreted as an integer/,
    /TypeError: an integer is required \(got type .*\)/,
    /RuntimeError: maximum recursion depth exceeded.*/,
    /IndexError: list assignment index out of range/,
    /TypeError: slice indices must be integers or None or have an __index__ method/,
    /TypeError: ord\(\) expected .*?, but .*? found/,
    /SyntaxError: '(.*?)' .*(outside|not.*in).*loop/,
    /SyntaxError: 'return' outside function/,
    /TypeError: can only concatenate list \(not .*\) to list/,
]

// Check if the given text or title matches any of the error messages
// Returns an array of the matches
const checkForMatch = (
    text: string,
    title: string
) => {
    const res: RegExp[] = [];
    for (const errMsg of commonErrors) {
        if (errMsg.test(text) || errMsg.test(title)) {
            res.push(errMsg)
        }
    }
    return res
}

// Update the error messages -> forum links map that a post has been updated
export const updateForumLinksMapOnUpdatePost = functions.firestore
    .document("forumData/{courseId}/forums/{forumId}/posts/{postId}")
    .onUpdate(
        async (snapshot: Change<QueryDocumentSnapshot>, context: EventContext) => {
            const forumId = context.params.forumId;
            const postId = context.params.postId;
            const { after } = snapshot;
            const isPrivate = after.get("isPrivate");
            const isDraft = after.get("isDraft");

            // If the post is private then make sure it is not in the forum links map
            if (isPrivate) {
                const db = admin.firestore();

                // Check all documents (which represent error message types) in the 'forumLinks' collection
                const querySnapshot = await db.collection("forumLinks").get();
                const docs = querySnapshot.docs;
                for (const doc of docs) {
                    const postIds = doc.data().postIds || [];

                    // If the post is in the list, remove it
                    if (postIds.includes(postId)) {
                        const updatedPostIds = postIds.filter((id: string) => id !== postId);
                        await doc.ref.update({ postIds: updatedPostIds });
                    }
                }

                // Nothing else to do
                return;
            }

            // Only update the forum links map with public, published posts to main
            if (forumId !== "main" || isPrivate || isDraft) return;

            // Determine whether this post contains a common error message
            const title = after.get("title");
            const text = after.get("contents").text;
            const matches = checkForMatch(text, title)

            // If there is a match, add it to the map in firestore
            if (matches.length > 0) {
                const db = admin.firestore();
                for (const errMsg of matches) {
                    const errMsgRef = db.collection("forumLinks").doc("" + errMsg);
                    await errMsgRef.set({
                        postIds: admin.firestore.FieldValue.arrayUnion(postId)
                    }, { merge: true })
                }
            }
        }
    )

// Update the error messages -> forum links map that a post has been deleted
export const updateForumLinksMapOnDeletePost = functions.firestore
    .document("forumData/{courseId}/forums/{forumId}/posts/{postId}")
    .onDelete(async (snapshot, context) => {
        const postId = context.params.postId;
        const db = admin.firestore();

        // Query all documents in the 'forumLinks' collection
        const querySnapshot = await db.collection("forumLinks").get();

        // Iterate through each document and remove the postId from its 'postIds' list
        const docs = querySnapshot.docs;
        for (const doc of docs) {
            // Get the existing postIds list or an empty array if it doesn't exist
            const postIds = doc.data().postIds || [];

            // Check if the postId exists in the list
            if (postIds.includes(postId)) {
                // Remove the postId from the list
                const updatedPostIds = postIds.filter((id: string) => id !== postId);

                // Update the document with the new postIds list
                await doc.ref.update({ postIds: updatedPostIds });
            }
        }
    }
    )

// Stores a new error message type for a user
export const updateErrorMessageType = functions.https.onCall(
    async (
        data: { userid: string; type: string },
        context
    ) => {
        functions.logger.info("Hello world from updateErrorMessageType!");
        const { userid, type } = data;
        const db = admin.firestore();
        await db.collection("error_message_types").doc(userid).set({ type: type });
        functions.logger.info("Should be updated!");
    }
);

// Get the error message type of a user
export const getErrorMessageType = functions.https.onCall(
    async (
        data: { userid: string },
        context
    ) => {
        functions.logger.info("Hello world from getErrorMessageType!");
        const { userid } = data;
        const db = admin.firestore();
        const userDoc = (await db.collection("error_message_types").doc(userid).get()).data();

        if (userDoc === undefined) {
            return "";
        }
        return userDoc.type;
    }
);
