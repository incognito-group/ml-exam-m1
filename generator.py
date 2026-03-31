#!/usr/bin/env python3

import csv
import os
from noeud import Noeud

def generate_dataset(max_depth=9, filename="dataset.csv"):
    """
    Generate tic-tac-toe dataset by running minimax algorithm
    Dataset contains only states where it's X's turn
    
    Args:
        max_depth: Maximum depth for minimax algorithm
        filename: Output CSV filename
    """
    # Create ressources directory if it doesn't exist
    os.makedirs("ressources", exist_ok=True)
    
    # Initialize root node
    root = Noeud()
    
    # Collect game data
    data_list = []
    
    # Run minimax with data collection
    print(f"Generating dataset with max depth {max_depth}...")
    Noeud.minimax_with_data(root, max_depth, Noeud.X, data_list)
    
    # Save to CSV file
    filepath = os.path.join("ressources", filename)
    with open(filepath, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header
        writer.writerow(Noeud.csv_header())
        
        # Write data rows
        for row in data_list:
            writer.writerow(row)
    
    print(f"Dataset generated with {len(data_list)} rows")
    print(f"Saved to {filepath}")
    
    # Print statistics
    x_wins_count = sum(1 for row in data_list if row[18] == 1)  # x_wins column
    draw_count = sum(1 for row in data_list if row[19] == 1)    # is_draw column
    o_wins_count = len(data_list) - x_wins_count - draw_count
    
    print("\nDataset Statistics:")
    print(f"  Total states: {len(data_list)}")
    print(f"  X wins: {x_wins_count} ({100*x_wins_count/len(data_list):.1f}%)")
    print(f"  Draws: {draw_count} ({100*draw_count/len(data_list):.1f}%)")
    print(f"  O wins: {o_wins_count} ({100*o_wins_count/len(data_list):.1f}%)")
    
    return filepath

if __name__ == "__main__":
    # Generate complete dataset
    generate_dataset(max_depth=9)
    
    print("\nDataset preview:")
    filepath = "ressources/dataset.csv"
    with open(filepath, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for i, row in enumerate(reader):
            if i < 6:  # Print first 5 rows + header
                print(row)
            else:
                break
