import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time

def plot_matrix():
    # Read the CSV file into a DataFrame
    df = pd.read_csv('parking_space.csv', header=None)

    # Plot the matrix using Matplotlib
    fig, ax = plt.subplots(figsize=(8, 8))  # Adjust the figsize as needed
    cax = ax.matshow(df.values, cmap='Blues_r', interpolation='nearest')  # Changed colormap to 'Blues_r'

    # Add white grid lines with thicker lines
    for i in range(len(df)+1):
        ax.axhline(i-0.5, color='black', linewidth=1)
        ax.axvline(i-0.5, color='black', linewidth=1)

    # Hide tick labels
    ax.set_xticks(np.arange(-0.5, len(df), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(df), 1), minor=True)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Add colorbar
    plt.colorbar(cax)

    # Set labels and title
    plt.xlabel('Column')
    plt.ylabel('Row')
    plt.title('Real Time Parking space')

    return fig

def main():
    st.title('Parking Space')

    # Initial plot
    fig = plot_matrix()
    plot_placeholder = st.empty()

    # Continuously update the plot
    while True:
        # Update the plot
        plot_placeholder.pyplot(fig)

        # Wait for a short duration before updating again
        time.sleep(5)  # Adjust the duration as needed

if __name__ == '__main__':
    main()
