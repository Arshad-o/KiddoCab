import re

def add_ui_driver_dashboard():
    filepath = 'lib/screens/driver_dashboard.dart'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # The block where Dark Mode is might be a good place.
    # Wait, the user already has Language, let's insert it after Language.
    anchor = """                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Language changed to $newValue')),
                          );
                        }
                      },
                    ),"""
                    
    new_ui = """                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Language changed to $newValue')),
                          );
                        }
                      },
                    ),
                    const Divider(),
                    ListenableBuilder(
                      listenable: AppSettings.instance,
                      builder: (context, _) {
                        return ListTile(
                          leading: const Icon(Icons.alarm, color: Colors.orange),
                          title: const Text('Pre-Trip Reminder'),
                          subtitle: const Text('How early to notify you before a trip'),
                          trailing: DropdownButton<int>(
                            value: AppSettings.instance.driverReminderMinutes,
                            underline: const SizedBox(),
                            icon: const Icon(Icons.arrow_drop_down),
                            items: const [
                              DropdownMenuItem(value: 5, child: Text('5 mins', style: TextStyle(fontSize: 14))),
                              DropdownMenuItem(value: 15, child: Text('15 mins', style: TextStyle(fontSize: 14))),
                              DropdownMenuItem(value: 30, child: Text('30 mins', style: TextStyle(fontSize: 14))),
                              DropdownMenuItem(value: 60, child: Text('1 hour', style: TextStyle(fontSize: 14))),
                              DropdownMenuItem(value: 120, child: Text('2 hours', style: TextStyle(fontSize: 14))),
                            ],
                            onChanged: (int? newValue) {
                              if (newValue != null) {
                                AppSettings.instance.setDriverReminderMinutes(newValue);
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(content: Text('Reminder set to $newValue minutes before trip')),
                                );
                              }
                            },
                          ),
                        );
                      }
                    ),"""
                    
    if "Pre-Trip Reminder" not in content:
        content = content.replace(anchor, new_ui)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

add_ui_driver_dashboard()
