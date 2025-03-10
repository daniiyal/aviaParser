class Flight:
    def __init__(self, flight_number, airline, aircraft_model, departure_point, arrival_point, departure_time, arrival_time, passenger_count):
        self.flight_number = flight_number
        self.airline = airline
        self.aircraft_model = aircraft_model
        self.departure_point = departure_point
        self.arrival_point = arrival_point
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.passenger_count = passenger_count

    def __repr__(self):
        return f"Flight({self.flight_number}, {self.airline}, {self.aircraft_model}, {self.departure_point}, {self.arrival_point}, {self.departure_time}, {self.arrival_time}, {self.passenger_count})"