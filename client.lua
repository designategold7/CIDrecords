ESX = exports["es_extended"]:getSharedObject()
local isWiring = false
local activeTarget = nil

-- Function to Draw "REC" Text
local function DrawRecText(freq)
    Citizen.CreateThread(function()
        while isWiring do
            Citizen.Wait(0)
            SetTextFont(4)
            SetTextScale(0.4, 0.4)
            SetTextColour(255, 0, 0, 255)
            SetTextEntry("STRING")
            AddTextComponentString("🔴 MONITORING CH: " .. freq)
            DrawText(0.90, 0.95)
        end
    end)
end

-- MAIN EVENT
RegisterNetEvent('esx_cidwire:useWire')
AddEventHandler('esx_cidwire:useWire', function()
    local playerPed = PlayerPedId()
    
    -- Check for closest player (The CI)
    local closestPlayer, closestDistance = ESX.Game.GetClosestPlayer()
    
    if closestPlayer ~= -1 and closestDistance <= 2.0 then
        -- PLANTING ON CI
        local targetId = GetPlayerServerId(closestPlayer)
        
        -- Play "Handover" Animation
        TaskStartScenarioInPlace(playerPed, "PROP_HUMAN_BUM_BIN", 0, true)
        ESX.ShowProgressBar("Planting Wire...", 2000)
        Citizen.Wait(2000)
        ClearPedTasks(playerPed)
        
        TriggerServerEvent('esx_cidwire:plantWire', targetId)
    else
        -- WEARING IT YOURSELF
        TriggerServerEvent('esx_cidwire:selfWire')
    end
end)

-- EVENT: WHEN YOU START MONITORING
RegisterNetEvent('esx_cidwire:startMonitoring')
AddEventHandler('esx_cidwire:startMonitoring', function(freq)
    isWiring = true
    ESX.ShowNotification("🎧 Wire Connected. Listening to Freq: " .. freq)
    
    -- Connect to the CALL channel (Hot Mic Channel)
    exports['pma-voice']:setCallChannel(freq)
    
    DrawRecText(freq)
end)

-- EVENT: WHEN YOU ARE THE CI (WEARING THE WIRE)
RegisterNetEvent('esx_cidwire:wearWire')
AddEventHandler('esx_cidwire:wearWire', function(freq)
    ESX.ShowNotification("🎙️ You are now wearing a hidden wire.")
    
    -- Force CI into the call channel (Hot Mic)
    exports['pma-voice']:setCallChannel(freq)
end)

-- EVENT: STOP EVERYTHING
RegisterNetEvent('esx_cidwire:stopWire')
AddEventHandler('esx_cidwire:stopWire', function()
    isWiring = false
    exports['pma-voice']:setCallChannel(0) -- Disconnect
    ESX.ShowNotification("⏹️ Wire Disconnected.")
end)