import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Authenticate Firebase Credentials
cred = credentials.Certificate("creds/Firebase-AdminSDK.json")

def initializeFirebase():
    try:
        firebase_admin.initialize_app(cred)
        print('Initialized Firebase connection.')

    except:
        print('App already exists.')

    # Secure connection to Firestore
    db = firestore.client()
    print('Initialized Firestore connection.')
    return db

def queryDocumentsFromCollection(path, key, operation, value, db):

  # Read database
  ref = db.collection(path)

  # Create a query against the collection
  query = ref.where(filter=firestore.FieldFilter(key, operation, value))

  return query.stream()

def addDocument(data, path, id, db):

  db.collection(path).document(id).set(data)

def updateDocument(data, path, id, db):

  db.collection(path).document(id).update(data)