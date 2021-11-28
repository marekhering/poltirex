from datetime import datetime, timedelta
from typing import Tuple, Optional

from app.models import Truck, Order, Route, Stretch
from app.utils import dist_calc


def find_closest_truck(a_lat: float, a_lon: float, start_time: datetime, end_time: datetime) -> Truck:
    closest_truck = None
    for truck in Truck.query.all():
        if truck.is_available(start_time, end_time):
            truck_distance = dist_calc(truck.position_lat, truck.position_lon, a_lat, a_lon)
            if closest_truck is None or closest_truck[0] > truck_distance:
                closest_truck = (truck_distance, truck)
    return closest_truck[1] if closest_truck is not None else None


def plan_stretch(a_lat: float, a_lon: float, b_lat: float, b_lon: float, start_time=None,
                 end_time=None) -> Tuple[datetime, datetime, Truck]:

    assert start_time is not None or end_time is not None
    dist = dist_calc(a_lat, a_lon, b_lat, b_lon)
    driving_time_hours = dist / Truck.MEAN_VELOCITY
    if start_time is None:
        start_time = end_time - timedelta(hours=driving_time_hours)
        start_time -= timedelta(seconds=start_time.second, microseconds=start_time.microsecond)

    else:  # end_time is None
        end_time = start_time + timedelta(hours=driving_time_hours)
        end_time -= timedelta(seconds=end_time.second, microseconds=end_time.microsecond)

    chosen_truck = find_closest_truck(a_lat, a_lon, start_time, end_time)
    return start_time, end_time, chosen_truck


def execute_order(order: Order) -> Optional[Tuple[Route, Stretch, Truck, Stretch, Truck]]:

    # Create stretches
    middle_point_lat = (order.departure_place_lat + order.destination_place_lat) / 2
    middle_point_lon = (order.departure_place_lon + order.destination_place_lon) / 2

    stretch_2_start_time, stretch_2_end_time, stretch_2_truck = plan_stretch(middle_point_lat, middle_point_lon,
                                                                             order.destination_place_lat,
                                                                             order.destination_place_lon,
                                                                             end_time=order.delivery_time)
    if stretch_2_truck is None:
        return None

    stretch_1_start_time, stretch_1_end_time, stretch_1_truck = plan_stretch(order.departure_place_lat,
                                                                             order.departure_place_lon,
                                                                             middle_point_lat, middle_point_lon,
                                                                             end_time=stretch_2_start_time)
    if stretch_1_truck is None:
        return None

    # Create route
    new_route = Route(start_datetime=stretch_1_start_time, end_datetime=stretch_2_end_time)
    order.route = new_route

    new_stretch_1 = Stretch(start_datetime=stretch_1_start_time, end_datetime=stretch_1_end_time,
                            start_place_lat=order.departure_place_lat, start_place_lon=order.departure_place_lon,
                            end_place_lat=middle_point_lat, end_place_lon=middle_point_lon,
                            route_id=new_route.id, truck_id=stretch_1_truck.id)

    new_stretch_2 = Stretch(start_datetime=stretch_2_start_time, end_datetime=stretch_2_end_time,
                            start_place_lat=middle_point_lat, start_place_lon=middle_point_lon,
                            end_place_lat=order.destination_place_lat, end_place_lon=order.destination_place_lon,
                            route_id=new_route.id, truck_id=stretch_1_truck.id)

    return new_route, new_stretch_1, stretch_1_truck, new_stretch_2, stretch_2_truck
