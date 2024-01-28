use framework "Cocoa"
on run argv
    set sourcePath to item 1 of argv
    set destPath to item 2 of argv
    set imageData to (current application's NSImage's alloc()'s initWithContentsOfFile:sourcePath)
    (current application's NSWorkspace's sharedWorkspace()'s setIcon:imageData forFile:destPath options:2)
    return
end run
