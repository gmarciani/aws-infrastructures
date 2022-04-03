def get_az_name(az: str, region_metadata: dict):
    if (
        region_metadata is None
        or region_metadata["AvailabilityZones"] is None
        or region_metadata["AvailabilityZones"][az] is None
    ):
        return az
    return region_metadata["AvailabilityZones"][az]
