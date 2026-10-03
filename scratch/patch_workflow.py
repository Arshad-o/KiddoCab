with open('.github/workflows/build-apk.yml', 'r') as f:
    content = f.read()
if "build_log.txt" not in content:
    content = content.replace("run: flutter build apk --release", "run: flutter build apk --release > build_log.txt 2>&1\n        continue-on-error: true")
    content += """
      - name: Upload Logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: Build-Logs
          path: build_log.txt
"""
with open('.github/workflows/build-apk.yml', 'w') as f:
    f.write(content)
