import 'package:flutter/material.dart';

class CabSelectionScreen extends StatefulWidget {
  const CabSelectionScreen({super.key});

  @override
  State<CabSelectionScreen> createState() => _CabSelectionScreenState();
}

class _CabSelectionScreenState extends State<CabSelectionScreen> {
  String _selectedTiming = 'Morning';

  final List<Map<String, dynamic>> _availableTrips = [
    {
      'driver': 'Michael T.',
      'rating': '4.9',
      'timing': 'Morning',
      'time': '07:30 AM',
      'from': 'Downtown Suburbs',
      'to': 'Oakwood Elementary',
      'seats': 3,
      'image': 'assets/images/driverimg.webp'
    },
    {
      'driver': 'Sarah J.',
      'rating': '4.8',
      'timing': 'Morning',
      'time': '08:15 AM',
      'from': 'Westside Apartments',
      'to': 'Lincoln High School',
      'seats': 1,
      'image': 'assets/images/driverimg.webp'
    },
    {
      'driver': 'Michael T.',
      'rating': '4.9',
      'timing': 'Afternoon',
      'time': '03:00 PM',
      'from': 'Oakwood Elementary',
      'to': 'Downtown Suburbs',
      'seats': 4,
      'image': 'assets/images/driverimg.webp'
    },
  ];

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    
    final filteredTrips = _availableTrips.where((trip) => trip['timing'] == _selectedTiming).toList();

    return Scaffold(
      backgroundColor: theme.colorScheme.background,
      appBar: AppBar(
        title: const Text('Find a KiddoCab'),
        backgroundColor: theme.colorScheme.primary,
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          // Filter Tabs
          Container(
            color: Colors.white,
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: ['Morning', 'Afternoon', 'Evening'].map((timing) {
                final isSelected = _selectedTiming == timing;
                return ChoiceChip(
                  label: Text(timing, style: TextStyle(fontWeight: FontWeight.bold, color: isSelected ? Colors.white : theme.colorScheme.primary)),
                  selected: isSelected,
                  selectedColor: theme.colorScheme.secondary,
                  backgroundColor: theme.colorScheme.primary.withOpacity(0.1),
                  onSelected: (selected) {
                    if (selected) setState(() => _selectedTiming = timing);
                  },
                );
              }).toList(),
            ),
          ),
          
          // Trip List
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: filteredTrips.length,
              itemBuilder: (context, index) {
                final trip = filteredTrips[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  elevation: 3,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Driver Info
                        Row(
                          children: [
                            CircleAvatar(
                              backgroundImage: AssetImage(trip['image']),
                              radius: 24,
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(trip['driver'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                                  Row(
                                    children: [
                                      const Icon(Icons.star, color: Colors.amber, size: 16),
                                      const SizedBox(width: 4),
                                      Text(trip['rating'], style: TextStyle(color: Colors.grey[700])),
                                    ],
                                  )
                                ],
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                              decoration: BoxDecoration(
                                color: theme.colorScheme.tertiary.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Text(
                                '\${trip['seats']} seats left',
                                style: TextStyle(color: theme.colorScheme.tertiary, fontWeight: FontWeight.bold),
                              ),
                            )
                          ],
                        ),
                        const Padding(
                          padding: EdgeInsets.symmetric(vertical: 12),
                          child: Divider(),
                        ),
                        // Route Info
                        Row(
                          children: [
                            Column(
                              children: [
                                Icon(Icons.circle, size: 12, color: theme.colorScheme.secondary),
                                Container(height: 30, width: 2, color: Colors.grey[300]),
                                Icon(Icons.location_on, size: 16, color: theme.colorScheme.primary),
                              ],
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(trip['from'], style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w500)),
                                  const SizedBox(height: 14),
                                  Text(trip['to'], style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                                ],
                              ),
                            ),
                            Text(
                              trip['time'],
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: theme.colorScheme.primary,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        // Action Button
                        SizedBox(
                          width: double.infinity,
                          child: ElevatedButton(
                            onPressed: () {
                              ScaffoldMessenger.of(context).showSnackBar(
                                const SnackBar(content: Text('Successfully assigned child to this route!')),
                              );
                              Navigator.pop(context);
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: theme.colorScheme.primary,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                            child: const Text('Assign Child to this Trip', style: TextStyle(fontSize: 16)),
                          ),
                        )
                      ],
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
