import os
import csv
import argparse
from typing import List

# Define the Courier class
class Courier:
    def __init__(self, courier_id: int, location: int, capacity: int):
        self.courier_id = courier_id
        self.location = location
        self.capacity = capacity

    def __repr__(self):
        return f"Courier(ID={self.courier_id}, Location={self.location}, Capacity={self.capacity})"


# Define the Delivery class
class Delivery:
    def __init__(self, delivery_id: int, capacity: int, pickup_loc: int, time_window_start: int, pickup_stacking_id: int, dropoff_loc: int):
        self.delivery_id = delivery_id
        self.capacity = capacity
        self.pickup_loc = pickup_loc
        self.time_window_start = time_window_start
        self.pickup_stacking_id = pickup_stacking_id
        self.dropoff_loc = dropoff_loc

    def __repr__(self):
        return f"Delivery(ID={self.delivery_id}, Capacity={self.capacity}, Pickup Loc={self.pickup_loc}, " \
               f"Time Window Start={self.time_window_start}, Pickup Stacking Id={self.pickup_stacking_id}, Dropoff Loc={self.dropoff_loc})"

class Instance:
    def __init__(self, instance_name: str, instance_path: str, couriers: List[Courier], deliveries: List[Delivery], travel_time):
        self.instance_name = instance_name
        self.instance_path = instance_path
        self.couriers = couriers
        self.deliveries = deliveries
        self.travel_time = travel_time
    
    def complexity(self) -> int:
        return len(self.couriers) * len(self.deliveries)

    def __repr__(self):
        return f"Instance({self.instance_name}, {len(self.couriers)} couriers, {len(self.deliveries)} deliveries)"

# Function to load couriers from CSV using the csv module
def load_couriers_from_csv(filepath):
    couriers = []
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            courier = Courier(
                courier_id=int(row['ID']),
                location=int(row['Location']),
                capacity=int(row['Capacity'])
            )
            couriers.append(courier)
    return couriers


# Function to load deliveries from CSV using the csv module
def load_deliveries_from_csv(filepath):
    deliveries = []
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            delivery = Delivery(
                delivery_id=int(row['ID']),
                capacity=int(row['Capacity']),
                pickup_loc=int(row['Pickup Loc']),
                time_window_start=int(row['Time Window Start']),
                pickup_stacking_id=int(row['Pickup Stacking_Id']),
                dropoff_loc=int(row['Dropoff Loc'])
            )
            deliveries.append(delivery)
    return deliveries


# # Function to load travel time matrix from CSV
# def load_travel_time_from_csv(filepath):
#     travel_time = []
#     with open(filepath, 'r') as file:
#         reader = csv.reader(file)
#         for row in reader:
#             if row[0] == 'Locations':
#                 travel_time.append([val for val in row])
#             else:
#                 travel_time.append([int(val) for val in row])  # Convert the row values to integers, skip the location index (first column)
#     return travel_time

# Function to load travel time matrix from CSV
def load_travel_time_from_csv(filepath):
  travel_time = []
  with open(filepath, 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header
    for row in reader:
      travel_time.append([int(val) for val in row[
                                              1:]])  # Convert the row values to integers, skip the location index (first column)
  return travel_time


# Function to process each instance folder and look for couriers.csv, deliveries.csv, and traveltime.csv
def process_instance_folder(instance_folder, instance_folder_path):
    couriers_file = None
    deliveries_file = None
    travel_time_file = None

    # Search for files in the instance folder
    for filename in os.listdir(instance_folder_path):
        if 'couriers.csv' in filename:
            couriers_file = os.path.join(instance_folder_path, filename)
        elif 'deliveries.csv' in filename:
            deliveries_file = os.path.join(instance_folder_path, filename)
        elif 'traveltimes.csv' in filename:
            travel_time_file = os.path.join(instance_folder_path, filename)

    # Ensure all necessary files are found
    if not couriers_file:
        raise FileNotFoundError(f"Missing couriers.csv file in folder: {instance_folder_path}")

    if not deliveries_file:
        raise FileNotFoundError(f"Missing deliveries.csv file in folder: {instance_folder_path}")

    if not travel_time_file:
        raise FileNotFoundError(f"Missing traveltimes.csv file in folder: {instance_folder_path}")


    # Load couriers, deliveries, and travel time matrix from the instance
    couriers = load_couriers_from_csv(couriers_file)
    deliveries = load_deliveries_from_csv(deliveries_file)
    travel_time = load_travel_time_from_csv(travel_time_file)

    return Instance(
                    instance_folder,
                    instance_folder_path,
                    couriers,
                    deliveries,
                    travel_time
                )

    return couriers, deliveries, travel_time


# Main function to loop through all instance folders
def process_all_instances(parent_folder) -> List[Instance]:
    all_instances = []

    # Loop through each instance folder in the parent directory
    for instance_folder in os.listdir(parent_folder):
        instance_folder_path = os.path.join(parent_folder, instance_folder)

        # Check if it's a directory (instance folder)
        if os.path.isdir(instance_folder_path):
            print(f"Processing instance: {instance_folder}")
            try:
                all_instances.append(process_instance_folder(instance_folder, instance_folder_path))

            except FileNotFoundError as e:
                print(e)

    return all_instances

def dump_instance_stats(parent_folder, instances: List[Instance]):
    file = open(parent_folder + "/stats.csv", "w")

    file.write(f"instance, couriers, deliveries, pickup_locations, dropoff_locations, stack_ids\n")
    for instance in instances:
        pickups = set(map(lambda d: d.pickup_loc, instance.deliveries))
        dropoffs = set(map(lambda d: d.dropoff_loc, instance.deliveries))
        stacking_ids = set(map(lambda d: d.pickup_stacking_id, instance.deliveries))

        file.write(f"{instance.instance_name},{len(instance.couriers)},{len(instance.deliveries)},{len(pickups)},{len(dropoffs)},{len(stacking_ids)}\n")

    file.close()


# Entry point of the script
def main():
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(description="Process couriers, deliveries, and travel time matrices from multiple instances.")
    parser.add_argument('parent_folder', type=str, help='Path to the parent folder containing all instance folders')
    parser.add_argument('--result-folder', required=False, type=str, help='Path to the folder where results are written', default='Challenge/results')

    args = parser.parse_args()

    # Process all instances
    all_instance_data = process_all_instances(args.parent_folder)


# Main execution
if __name__ == "__main__":
    main()
