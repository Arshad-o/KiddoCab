class LocationData {
  static const Map<String, Map<String, List<String>>> indiaRegions = {
    'Telangana': {
      'Hyderabad': ['Ameerpet', 'Banjara Hills', 'Jubilee Hills', 'Khairatabad', 'Secunderabad', 'Madhapur', 'Gachibowli'],
      'Rangareddy': ['Serilingampally', 'Rajendranagar', 'Saroornagar', 'Shamshabad', 'Ibrahimpatnam'],
      'Medchal-Malkajgiri': ['Medchal', 'Malkajgiri', 'Kukatpally', 'Quthbullapur', 'Uppal'],
      'Warangal': ['Warangal', 'Hanamkonda', 'Kazipet'],
      'Nizamabad': ['Nizamabad South', 'Nizamabad North', 'Armoor', 'Bodhan'],
    },
    'Andhra Pradesh': {
      'Visakhapatnam': ['Bheemunipatnam', 'Anandapuram', 'Padmanabham', 'Pendurthi'],
      'Vijayawada (NTR)': ['Vijayawada Rural', 'Vijayawada Urban', 'Ibrahimpatnam', 'Mylavaram'],
      'Guntur': ['Guntur East', 'Guntur West', 'Mangalagiri', 'Tenali'],
    },
    'Karnataka': {
      'Bengaluru Urban': ['Bengaluru North', 'Bengaluru South', 'Bengaluru East', 'Anekal'],
      'Mysuru': ['Mysuru', 'Nanjangud', 'T. Narasipura'],
    }
  };

  static List<String> getStates() => indiaRegions.keys.toList();
  static List<String> getDistricts(String state) => indiaRegions[state]?.keys.toList() ?? [];
  static List<String> getMandals(String state, String district) => indiaRegions[state]?[district] ?? [];
}
