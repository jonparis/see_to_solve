tell application "Terminal"
	activate
	do script "echo 'Starting See to Solve service...' && echo 'The service will run in this window. Keep this window open to keep the service running.' && echo 'To stop the service, close this window or press Ctrl+C.' && echo '' && cd \"" & (POSIX path of (path to me as text)) & "\" && source ../venv/bin/activate && ./see_to_solve_service_mac.sh"
end tell

tell application "System Events"
	set appName to "See to Solve Service"
	
	-- Create the application icon
	set iconPath to (POSIX path of (path to me as text)) & "/see_to_solve_chrome_ext/assets/icon-128.png"
	
	-- Set the application icon
	tell process appName
		set value of attribute "AXIcon" to iconPath
	end tell
end tell 