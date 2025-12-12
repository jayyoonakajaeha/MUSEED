
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.ml.recommendation import build_user_index, USER_INDEX, get_similar_users
from app import models

def test_user_index():
    db = SessionLocal()
    try:
        print("1. Triggering User Index Build...")
        build_user_index(db)
        
        from app.ml.recommendation import USER_INDEX
        
        if USER_INDEX is not None:
            print(f"✅ User Index successfully built.")
            print(f"   Total Vectors: {USER_INDEX.ntotal}")
            
            # Test Search
            user = db.query(models.User).first()
            if user:
                print(f"\n2. Testing Similarity Search for User ID {user.id} ({user.username})...")
                recommendations = get_similar_users(db, user.id, limit=3)
                print(f"   Found {len(recommendations)} recommendations:")
                for rec in recommendations:
                    print(f"   - User {rec['user'].username}: Similarity {rec['similarity']:.4f}")
            else:
                print("   No users found to test search.")
        else:
            print("❌ User Index failed to build (USER_INDEX is None).")
            
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_user_index()
