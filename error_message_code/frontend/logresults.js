import { firestore } from "firebaseApp";
import { serverTimestamp } from "firebase/firestore";

// Log the results of this run to firebase - can always add more to this
export const logCodeRun = (userId, projectData, code, unitTestResults, results) => {
    firestore.collection('ide_logs_v2')
        .doc(userId)
        .collection('logs')
        .doc(new Date().toISOString())
        .set({
            projectData: projectData,
            code: code,
            unitTestResults: unitTestResults,
            codeRunResults: results,
            serverTimestamp: serverTimestamp() // This is the real timestamp to use
        })
        .then(() => {
            console.log('Document successfully updated/appended!');
        })
        .catch((error) => {
            console.error('Error updating/appending document to ide_logs_v2: ', error);
        });
}