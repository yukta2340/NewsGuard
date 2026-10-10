# data_loader.py
import os
import pandas as pd

def load_dataset(file_path=None):
    """
    Loads dataset from CSV files if present, or dynamically uses the comprehensive
    multi-domain news dataset from train_advanced_model.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fake_path = os.path.join(base_dir, 'data', 'Fake.csv')
    true_path = os.path.join(base_dir, 'data', 'True.csv')

    if os.path.exists(fake_path) and os.path.exists(true_path):
        try:
            df_fake = pd.read_csv(fake_path)
            df_fake['label'] = 'FAKE'
            df_true = pd.read_csv(true_path)
            df_true['label'] = 'REAL'
            df = pd.concat([df_fake, df_true], ignore_index=True)
            df = df.sample(frac=1, random_state=42).reset_index(drop=True)
            print(f"Loaded dataset from CSV files: {len(df)} total rows.")
            return df
        except Exception as e:
            print(f"Warning: Failed to parse CSV files: {e}")

    # Fallback to rich built-in multi-domain dataset
    print("Loading comprehensive multi-domain training dataset...")
    try:
        from train_advanced_model import generate_augmented_dataset
        df = generate_augmented_dataset()
        df['title'] = df['text']
        print(f"Loaded verified training dataset with {len(df)} samples.")
        return df
    except Exception as e:
        print(f"Error loading training data: {e}")
        return None

def get_data_for_training(df):
    """
    Prepares text (X) and label (y) for model training.
    """
    if df is None:
        return None, None

    if 'full_text' not in df.columns:
        if 'title' in df.columns and 'text' in df.columns and df['title'].iloc[0] != df['text'].iloc[0]:
            df['full_text'] = df['title'].fillna('') + ' ' + df['text'].fillna('')
        elif 'text' in df.columns:
            df['full_text'] = df['text'].fillna('')
        else:
            df['full_text'] = df['title'].fillna('')

    X = df['full_text']
    y = df['label']

    print("Data prepared for training: X (full_text) and y (label).")
    return X, y
