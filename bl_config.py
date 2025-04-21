import os
import time
import subprocess
import random
import profiles

class config :

    @staticmethod
    def changeProfile(config_path,instance_name="Tiramisu64"): 
        profile = random.choice(profiles.DEVICE_PROFILES)
        manufacturer = profile['manufacturer']
        brand = profile['brand']
        model = profile['model']
        screen_width = profile['screen_width']
        screen_height = profile['screen_height']
        
        try:
            if not os.path.exists(config_path):
                print("[-] BlueStacks config file not found.")
                return False

            # Read existing config
            with open(config_path, "r", encoding="utf-8") as file:
                config_data = file.readlines()

            # Modify the relevant lines
            new_config = []
            for line in config_data:
                if f"bst.instance.{instance_name}.device_custom_manufacturer" in line:
                    new_config.append(f'bst.instance.{instance_name}.device_custom_manufacturer="{manufacturer}"\n')
                elif f"bst.instance.{instance_name}.device_custom_brand" in line:
                    new_config.append(f'bst.instance.{instance_name}.device_custom_brand="{brand}"\n')
                elif f"bst.instance.{instance_name}.device_custom_model" in line:
                    new_config.append(f'bst.instance.{instance_name}.device_custom_model="{model}"\n')
                elif f"bst.instance.{instance_name}.device_profile_code" in line:
                    new_config.append(f'bst.instance.{instance_name}.device_profile_code="custom"\n')
                elif "bst.custom_resolutions" in line:
                    new_config.append(f'bst.custom_resolutions="{screen_width} x {screen_height}"\n')
                    
                elif f"bst.instance.{instance_name}.fb_height" in line:
                    new_config.append(f'bst.instance.{instance_name}.fb_height="{screen_width}"\n')
                elif f"bst.instance.{instance_name}.fb_width" in line:
                    new_config.append(f'bst.instance.{instance_name}.fb_width="{screen_height}"\n')
                else:
                    new_config.append(line)

            # Write back the modified config
            with open(config_path, "w", encoding="utf-8") as file:
                file.writelines(new_config)

            print(f"[✅] Successfully changed BlueStacks profile to:")
            print(f"    📌 Manufacturer: {manufacturer}")
            print(f"    📌 Model: {model}")
            print(f"    📌 Screen Resolution: {screen_width}x{screen_height}")

            return True

        except Exception as e:
            print(f"[-] Error modifying BlueStacks settings: {e}")
            return False
   
    @staticmethod
    def is_google_acount(config_path,instance_name="Tiramisu64"):
        try:
            if not os.path.exists(config_path):
                print("[-] BlueStacks config file not found.")
                return False

            with open(config_path, "r", encoding="utf-8") as file:
                config_data = file.readlines()

            for line in config_data:
                if f"bst.instance.{instance_name}.google_account_logins" in line:
                    email = line.split("=")[1].strip().strip('"')
                    if email:
                        print(f"[✅] Google account found: {email}")
                        return True
                    else:
                        print("[❌] No Google account registered.")
                        return False
            
            print("[❌] Google account setting not found in the config.")
            return False
        except Exception as e:
            print(f"[-] Error checking Google account: {e}")
            return False
    
    @staticmethod
    def set_adb_access(config_path,enable=True):
        try:
            if not os.path.exists(config_path):
                print("[-] BlueStacks config file not found.")
                return False

            # Read existing config
            with open(config_path, "r", encoding="utf-8") as file:
                config_data = file.readlines()

            # Modify the ADB access setting
            new_config = []
            for line in config_data:
                if "bst.enable_adb_access" in line:
                    new_config.append(f'bst.enable_adb_access="1"\n' if enable else 'bst.enable_adb_access="0"\n')
                else:
                    new_config.append(line)

            # Write back the modified config
            with open(config_path, "w", encoding="utf-8") as file:
                file.writelines(new_config)

            print(f"[✅] ADB access {'enabled' if enable else 'disabled'} successfully!")

            # Restart BlueStacks to apply changes
            #restart_bluestacks()
            return True

        except Exception as e:
            print(f"[-] Error modifying ADB settings: {e}")
            return False
        
    @staticmethod
    def change_resolution(config_path,instance_name="Tiramisu64",screen_width="1920",screen_height="1080"):  
        try:
            if not os.path.exists(config_path):
                print("[-] BlueStacks config file not found.")
                return False

            # Read existing config
            with open(config_path, "r", encoding="utf-8") as file:
                config_data = file.readlines()

            # Modify the relevant lines
            new_config = []
            for line in config_data:
                if "bst.custom_resolutions" in line:
                    new_config.append(f'bst.custom_resolutions="{screen_width} x {screen_height}"\n')
                elif f"bst.instance.{instance_name}.fb_height" in line:
                    new_config.append(f'bst.instance.{instance_name}.fb_height="{screen_height}"\n')
                elif f"bst.instance.{instance_name}.fb_width" in line:
                    new_config.append(f'bst.instance.{instance_name}.fb_width="{screen_width}"\n')
                else:
                    new_config.append(line)

            # Write back the modified config
            with open(config_path, "w", encoding="utf-8") as file:
                file.writelines(new_config)

            print(f"[✅] Successfully changed Resolution profile to:")
            print(f"    📌 Screen Resolution: {screen_width}x{screen_height}")

            #restart_bluestacks()
            return True

        except Exception as e:
            print(f"[-] Error modifying BlueStacks settings: {e}")
            return False

        
