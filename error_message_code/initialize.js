import { firestore } from "firebaseApp"
import { errorMessageTypes } from "./errorMessageTypes"
import { serverTimestamp } from "firebase/firestore"

// Initialize the error message type
export const initSelectedErrorMessageType = (userId, setSelectedErrorMessageType) => {
    const userRef = firestore.collection('error_message_types').doc(userId);
    const typesRef = userRef.collection('types_v2');

    // Grab the latest error message type using the serverTimestamp
    typesRef.orderBy("timestamp_v2", "desc").limit(1).get().then((querySnapshot) => {
        if (!querySnapshot.empty) {
            const latestType = querySnapshot.docs[0].data().type;
            setSelectedErrorMessageType(latestType)
        } else {
            // Grab the latest error message type from firestore using the old timestamp
            typesRef.orderBy("timestamp", "desc").limit(1).get().then((querySnapshot) => {
                if (!querySnapshot.empty) {
                    const latestType = querySnapshot.docs[0].data().type;
                    setSelectedErrorMessageType(latestType)

                } else {
                    // There was not a stored error message type, so generate one
                    const type = generateRandomErrorMessageType();
                    setSelectedErrorMessageType(type)
                    storeErrorMessageType(userId, type)
                }
            })
        }
    }).catch((error) => {
        console.error("Error getting types:", error);
    });
}

const generateRandomErrorMessageType = () => {
    const index = Math.floor(Math.random() * errorMessageTypes.length);
    return errorMessageTypes[index].value;
}

// Store the error message type in firestore
export const storeErrorMessageType = (userId, errorType) => {
    const userRef = firestore.collection('error_message_types').doc(userId);
    const typesRef = userRef.collection('types_v2');

    // Add a new type with a timestamp
    const timestamp = new Date().toISOString();
    const timestamp_v2 = serverTimestamp();
    typesRef.add({
        type: errorType,
        timestamp: timestamp,
        timestamp_v2: timestamp_v2
    });
}