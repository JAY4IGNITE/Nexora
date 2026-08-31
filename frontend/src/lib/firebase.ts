import { initializeApp } from 'firebase/app';
import { getAuth, onAuthStateChanged as firebaseOnAuthStateChanged } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID
};

export const app = initializeApp(firebaseConfig);

const isMock = firebaseConfig.apiKey === 'mock-api-key';

export const auth = isMock 
  ? {
      currentUser: null,
      signOut: () => Promise.resolve()
    } as unknown as ReturnType<typeof getAuth> 
  : getAuth(app);

export const onAuthStateChanged = isMock
  ? (_authObj: any, cb: any) => { cb(null); return () => {}; }
  : firebaseOnAuthStateChanged;
