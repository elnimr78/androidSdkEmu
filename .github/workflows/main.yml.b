name: Android Emulator Logcat

on:
  workflow_dispatch:

jobs:
  emulator-logcat:
    runs-on: windows-latest
    env:
      ANDROID_SDK_ROOT: ${{ github.workspace }}\android-sdk
      ANDROID_HOME: ${{ github.workspace }}\android-sdk
      EMULATOR_NAME: test-emulator

    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Set up environment variables
        run: |
          echo "ANDROID_SDK_ROOT=${{ env.ANDROID_SDK_ROOT }}" >> $env:GITHUB_ENV
          echo "ANDROID_HOME=${{ env.ANDROID_HOME }}" >> $env:GITHUB_ENV

      - name: Download Android SDK command line tools
        run: |
          Invoke-WebRequest https://dl.google.com/android/repository/commandlinetools-win-9477386_latest.zip -OutFile cmdline-tools.zip
          Expand-Archive cmdline-tools.zip -DestinationPath "$env:ANDROID_SDK_ROOT\temp"
          mkdir "$env:ANDROID_SDK_ROOT\cmdline-tools\latest" -Force
          Move-Item "$env:ANDROID_SDK_ROOT\temp\cmdline-tools\*" "$env:ANDROID_SDK_ROOT\cmdline-tools\latest"
        shell: pwsh

      - name: Add SDK tools to PATH
        run: |
          echo "$env:ANDROID_SDK_ROOT\cmdline-tools\latest\bin" >> $env:GITHUB_PATH
          echo "$env:ANDROID_SDK_ROOT\platform-tools" >> $env:GITHUB_PATH
          echo "$env:ANDROID_SDK_ROOT\emulator" >> $env:GITHUB_PATH
        shell: pwsh

      - name: Accept Android SDK licenses
        run: |
          mkdir -p "$env:ANDROID_SDK_ROOT\licenses"
          echo "24333f8a63b6825ea9c5514f83c2829b004d1fee" > "$env:ANDROID_SDK_ROOT\licenses\android-sdk-license"
          echo "84831b9409646a918e30573bab4c9c91346d8abd" > "$env:ANDROID_SDK_ROOT\licenses\android-sdk-preview-license"
        shell: pwsh

      - name: Set up Java 11
        uses: actions/setup-java@v3
        with:
          distribution: 'temurin'
          java-version: '11'

      - name: Install required Android SDK components
        run: |
          $ErrorActionPreference = "Stop"
          & "$env:ANDROID_SDK_ROOT\cmdline-tools\latest\bin\sdkmanager.bat" --sdk_root="$env:ANDROID_SDK_ROOT" "platform-tools" "emulator" "system-images;android-30;google_apis;x86_64"
          & "$env:ANDROID_SDK_ROOT\cmdline-tools\latest\bin\sdkmanager.bat" --licenses
        shell: pwsh

      - name: List installed SDK components
        run: |
          & "$env:ANDROID_SDK_ROOT\cmdline-tools\latest\bin\sdkmanager.bat" --list_installed
        shell: pwsh

      - name: Create Emulator
        run: |
          echo no | & "$env:ANDROID_SDK_ROOT\cmdline-tools\latest\bin\avdmanager.bat" create avd -n $env:EMULATOR_NAME -k "system-images;android-30;google_apis;x86_64" --force --device "pixel"
        shell: pwsh

      - name: Start Emulator
        run: |
          $env:EMULATOR_NAME = "${{ env.EMULATOR_NAME }}"
          Start-Process -NoNewWindow -FilePath "$env:ANDROID_SDK_ROOT\emulator\emulator.exe" -ArgumentList "-avd $env:EMULATOR_NAME -memory 2048 -cores 2 -no-snapshot -no-audio -no-window -gpu swiftshader_indirect"
          Start-Sleep -Seconds 60
        shell: pwsh

      - name: Wait for device
        run: |
          adb wait-for-device
        shell: pwsh

      - name: Logcat Output
        run: |
          adb logcat -d > logcat_output.txt
        shell: pwsh

      - name: Upload Logcat Output
        uses: actions/upload-artifact@v4
        with:
          name: logcat-output
          path: logcat_output.txt
