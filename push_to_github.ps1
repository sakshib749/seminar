param(
    [string]$repoName = "Phishing-Website-Detection-by-Machine-Learning-Techniques",
    [string]$description = "Phishing Website Detection by Machine Learning Techniques",
    [string]$visibility = "public",
    [string]$remote = "origin",
    [switch]$UseGH
)

Write-Host "Preparing to push repository to GitHub..."

# Check if inside a git repo
$insideGit = (git rev-parse --is-inside-work-tree) 2>$null
if (-not $insideGit) {
    Write-Host "Initializing a new git repository..."
    git init
    git add --all
    git commit -m "Initial commit"
} else {
    Write-Host "Git repository already initialized."
}

# Prefer GitHub CLI if requested and available
if ($UseGH -and (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Host "Creating repository using GitHub CLI (gh)..."
    gh repo create $repoName --$visibility --description "$description" --source=. --remote=$remote --push
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Repository created and pushed via gh successfully."
        return
    } else {
        Write-Host "gh failed or was cancelled. Falling back to manual git commands."
    }
}

# If gh not used or not available, print instructions and try to add remote if provided
Write-Host "\nIf you want this script to create the remote repo for you, install GitHub CLI and re-run with -UseGH."
Write-Host "Attempting to add remote and push. If remote doesn't exist you'll need to create it on GitHub and re-run these commands.\n"

$cwd = Get-Location
$remoteUrl = Read-Host "Enter your remote repo URL (e.g. https://github.com/username/$repoName.git) or leave blank to only show commands"

if ($remoteUrl) {
    Write-Host "Adding remote '$remote' -> $remoteUrl"
    git remote add $remote $remoteUrl 2>$null
    git branch -M main 2>$null
    git push -u $remote main
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Pushed to $remote successfully."
        return
    } else {
        Write-Host "Push failed. Please check credentials and remote URL.\n"
    }
}

Write-Host "Manual commands you can run to create and push the repo:" 
Write-Host "git init"
Write-Host "git add --all"
Write-Host "git commit -m 'Initial commit'"
Write-Host "git branch -M main"
Write-Host "git remote add origin https://github.com/<your-username>/$repoName.git"
Write-Host "git push -u origin main"

Write-Host "\nOr install GitHub CLI and run: gh repo create $repoName --$visibility --description \"$description\" --source=. --remote=$remote --push"
