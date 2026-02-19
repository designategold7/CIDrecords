ESX = exports["es_extended"]:getSharedObject()

-- CONFIG
local wireFrequency = 9119 -- Or generate random math.random(1000,9999)

ESX.RegisterUsableItem('cid_wire', function(source)
    TriggerClientEvent('esx_cidwire:useWire', source)
end)

-- PLANTING LOGIC
RegisterNetEvent('esx_cidwire:plantWire')
AddEventHandler('esx_cidwire:plantWire', function(targetId)
    local src = source
    local xPlayer = ESX.GetPlayerFromId(src)
    local xTarget = ESX.GetPlayerFromId(targetId)

    if xTarget then
        -- 1. Put the Detective (Source) in the channel to LISTEN
        TriggerClientEvent('esx_cidwire:startMonitoring', src, wireFrequency)
        
        -- 2. Put the CI (Target) in the channel to TRANSMIT
        TriggerClientEvent('esx_cidwire:wearWire', targetId, wireFrequency)
        
        -- 3. Notification
        xPlayer.showNotification("Wire planted on " .. xTarget.getName())
    else
        xPlayer.showNotification("Target not found.")
    end
end)

-- SELF WEAR LOGIC
RegisterNetEvent('esx_cidwire:selfWire')
AddEventHandler('esx_cidwire:selfWire', function()
    local src = source
    TriggerClientEvent('esx_cidwire:wearWire', src, wireFrequency)
    TriggerClientEvent('esx_cidwire:startMonitoring', src, wireFrequency)
end)