"""
BurnoutBuddy - First-time setup script
Run this once to install dependencies and train the model.
"""
import subprocess
import sys
import os

def main():
    print("🌸 Welcome to BurnoutBuddy Setup!")
    print("=" * 40)

    print("\n📦 Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    print("\n🤖 Training the ML model...")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    from data.generate_data import generate_dataset
    generate_dataset()

    from models.train_model import train_model
    _, _, acc = train_model()
    print(f"\n✅ Model trained! Accuracy: {acc*100:.1f}%")

    print("\n🚀 Setup complete! Run app.py to start BurnoutBuddy.")
    print("   python app.py")

if __name__ == "__main__":
    main()
