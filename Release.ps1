param (
    [string]$ProductionBranch = "Production",
    [string]$MainBranch = "master"
)

& git checkout $ProductionBranch && git merge $MainBranch && git push origin $ProductionBranch && git checkout $MainBranch