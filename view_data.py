from app import display_raw_data, display_transformed_data

def display_data():
    """
    Allows the user to choose between viewing raw data or transformed data.
    """
    while True:
        print("Choose data to display:")
        print("1. Raw Data")
        print("2. Transformed Data")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            # Display raw data
            raw_data = display_raw_data()
            print("Raw Data:")
            for row in raw_data:
                print(row)
        elif choice == '2':
            # Display transformed data
            transformed_data = display_transformed_data()
            print("Transformed Data:")
            for row in transformed_data:
                print(row)
        elif choice == '3':
            # Exit the program
            print("Exiting program.")
            break
        else:
            # Handle invalid input
            print("Invalid choice. Please enter 1, 2, or 3.")


display_data()