function [] = fall()
    % ThingSpeak credentials and channel information
    channelID = 2564278;  % Replace with your channel ID
    writeKey = 'RM41JJ3PW1IF0CUB';  % Replace with your write key

    % Field mapping
    field1 = 1;  % For motion history image average
    field2 = 2;  % For motion speed gauge
    field3 = 3;  % For fall detection lamp

    % Other settings
    lampRedValue = 1;  % Value to set the lamp to red
    lampGreenValue = 0;  % Value to set the lamp to green

    % Reading the FALL video
    vidFile = "C:/Users/lenovo/Documents/MATLAB/Indust/falling.mp4";
    vid = VideoReader(vidFile);

    % Initializing foreground and blob detectors
    detector = vision.ForegroundDetector('NumTrainingFrames', 10, 'NumGaussians', 5, ...
                                         'MinimumBackgroundRatio', 0.7, 'InitialVariance', 0.05, ...
                                         'LearningRate', 0.0002);
    blob = vision.BlobAnalysis('CentroidOutputPort', true, 'AreaOutputPort', true, ...
                               'BoundingBoxOutputPort', true, 'MinimumBlobArea', 500);

    % Duration of motion history image
    tmhi = 15;

    % Strel parameters
    strelType = 'square';
    strelSize = 5;

    frameNo = 0;

    % Initialize log data
    logData = [];

    while hasFrame(vid)  % Process the entire video
        frame = readFrame(vid);
        frameNo = frameNo + 1;

        % Assigning initial value to motion history image
        if frameNo == 1
            mhimage = zeros(size(frame, 1), size(frame, 2));
        end

        % Detecting foreground mask
        fgMask = step(detector, frame);
        % Modifying mask to close gaps and fill holes
        fgClose = modifyMask(fgMask, strelType, strelSize);

        % Finding largest blob
        [area, centroid, box] = step(blob, fgClose);
        pos = find(area == max(area));
        box = box(pos, :);

        if ~isempty(box)
            % Mask after inside bounding box
            fgBBox = maskInsideBBox(fgClose, box);
            % Calculate motion history image
            mhimage = calcSpeed(mhimage, fgBBox, tmhi);

            % Calculate motion speed (e.g., sum of changes in mhimage)
            motionSpeed = sum(mhimage(:)) / numel(mhimage);

            % Detect if a fall has occurred
            isFallen = detectFall(mhimage);

            % Log data
            logData = [logData; frameNo, motionSpeed, isFallen];

            % Debug output
            fprintf('Frame %d: motionSpeed = %f, isFallen = %d\n', frameNo, motionSpeed, isFallen);

            % Take action based on fall status
            if isFallen
                % Action if the person is fallen
                fprintf('Person is fallen.\n');
                % Add code here to perform specific actions for a fallen person
            else
                % Action if the person is standing
                fprintf('Person is standing.\n');
                % Add code here to perform specific actions for a standing person
            end

            % Throttle updates to ThingSpeak to every 450 frames (approximately 15 seconds at 30 fps)
            if mod(frameNo, 450) == 0
                try
                    % Update ThingSpeak channel
                    response = thingSpeakWrite(channelID, 'Fields', [field1, field2, field3], ...
                        'Values', {mean(mhimage(:)), motionSpeed, isFallen * lampRedValue + ~isFallen * lampGreenValue}, ...
                        'WriteKey', writeKey);
                    fprintf('ThingSpeak update response: %s\n', response);
                catch ME
                    fprintf('Error updating ThingSpeak: %s\n', ME.message);
                end
            end
        end

        drawnow;  % Ensure the plots are updated
    end

    % Release resources
    release(detector);
    release(blob);

    % Save log data to a CSV file
    csvwrite('fall_detection_log.csv', logData);

    % Print a summary
    fprintf('Processing complete. Data saved to fall_detection_log.csv.\n');
end

% Supporting functions
function fgClose = modifyMask(fgMask, strelType, strelSize)
    se = strel(strelType, strelSize);
    fgClose = imclose(fgMask, se);
end

function fgBBox = maskInsideBBox(fgMask, bbox)
    fgBBox = fgMask;
    fgBBox(1:bbox(2), :) = 0;
    fgBBox(bbox(2) + bbox(4):end, :) = 0;
    fgBBox(:, 1:bbox(1)) = 0;
    fgBBox(:, bbox(1) + bbox(3):end) = 0;
end

function mhimage = calcSpeed(mhimage, fgBBox, tmhi)
    timestamp = 1;  % Incrementing timestamp

    % Update motion history image
    mhimage(fgBBox) = timestamp;

    % Update timestamp for each frame
    mhimage(mhimage > 0) = mhimage(mhimage > 0) + 1;

    % Reset expired pixels to zero
    mhimage(mhimage >= tmhi) = 0;
end

function fallen = detectFall(mhimage)
    % Example: if there is a significant area with a high motion value, consider it a fall
    threshold = 0.5 * max(mhimage(:));  % Adjust threshold as needed
    fallen = any(mhimage(:) > threshold);
end
