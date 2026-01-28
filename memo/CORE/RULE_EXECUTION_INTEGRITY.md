# ONI SAFETY PROTOCOL: EXECUTION INTEGRITY
# User Rule: "Never leave a script running and leave the chat without outcome commitment."
# Implication: Always verify the FINAL line of an execution log before NotifyUser.

function Verify-Execution {
    param($LastExitCode, $ErrorBuffer)
    if ($LastExitCode -ne 0 -or $ErrorBuffer) {
        Write-Error "Execution Failed. Do NOT report success."
        exit 1
    }
}
