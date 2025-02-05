equipment_profiles = {
    "Grainfather G30": {
        "xml": """
        <EQUIPMENT>
            <NAME>Grainfather G30</NAME>
            <VERSION>1</VERSION>
            <BOIL_SIZE>27</BOIL_SIZE>
            <BATCH_SIZE>23</BATCH_SIZE>
            <TRUB_CHILLER_LOSS>1</TRUB_CHILLER_LOSS>
            <LAUTER_DEADSPACE>3.5</LAUTER_DEADSPACE>
            <BOIL_TIME>60</BOIL_TIME>
            <HOP_UTILIZATION>100</HOP_UTILIZATION>
            <EVAP_RATE>7.4074074074074066</EVAP_RATE>
            <CALC_BOIL_VOLUME>true</CALC_BOIL_VOLUME>
        </EQUIPMENT>
        """,
        "params": {
            "batch_size": 23.0,
            "boil_size": 27.0,
            "boil_time": 60,
            "efficiency": 75,
            "evap_rate": 7.4,
            "trub_loss": 1,
            "deadspace": 3.5
        }
    },
    # Här kan vi lägga till fler bryggverksprofiler i framtiden.
}

def get_equipment_profile(profile_name):
    return equipment_profiles.get(profile_name, None)
