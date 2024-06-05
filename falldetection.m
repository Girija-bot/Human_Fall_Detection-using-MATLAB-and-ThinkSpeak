function [] = falldetection()

% Reading the FALL video
vid = vision.VideoFileReader("C:/Users/lenovo/Documents/MATLAB/Indust/falling.mp4");

% Initializing foreground and blob detectors
detector = vision.ForegroundDetector(...
    'NumTrainingFrames', 10, 'NumGaussians', 5, ...
    'MinimumBackgroundRatio', 0.7, 'InitialVariance', 0.05, ...
    'LearningRate', 0.0002);
blob = vision.BlobAnalysis(...
    'CentroidOutputPort', true, 'AreaOutputPort', true, ...
    'BoundingBoxOutputPort', true, ...
    'MinimumBlobAreaSource', 'Property', 'MinimumBlobArea', 500);

% Duration of motion history image
tmhi = 15;

% Strel parameters
strelType = 'square';
strelSize = 5;

frameNo = 0;
while ~isDone(vid) % Process the entire video
    frame = step(vid);
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
        
        % Output
        subplot(1, 3, 1);
        imshow(frame);
        title(sprintf('Original Video\nFrame no - %d', frameNo), 'FontSize', 20);
        
        subplot(1, 3, 2);
        imshow(fgMask);
        title(sprintf('Human detection\nFrame no - %d', frameNo), 'FontSize', 20);
        
        subplot(1, 3, 3);
        imshow(uint8((mhimage * 255) / tmhi));
        title(sprintf('Motion History Image\nFrame no - %d', frameNo), 'FontSize', 20);
    else
        % Output
        subplot(1, 3, 1);
        imshow(frame);
        title(sprintf('Original Video\nFrame no - %d', frameNo), 'FontSize', 20);
        
        subplot(1, 3, 2);
        imshow(fgMask);
        title(sprintf('Human detection\nFrame no - %d', frameNo), 'FontSize', 20);
        
        subplot(1, 3, 3);
        imshow(uint8((mhimage * 255) / tmhi));
        title(sprintf('Motion History Image\nFrame no - %d', frameNo), 'FontSize', 20);
    end
    
    drawnow; % Ensure the plots are updated
end

% Release resources
release(vid); % Release the video reader

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
    timestamp = 1; % Incrementing timestamp

    % Update motion history image
    mhimage(fgBBox) = timestamp;

    % Update timestamp for each frame
    mhimage(mhimage > 0) = mhimage(mhimage > 0) + 1;
    
    % Reset expired pixels to zero
    mhimage(mhimage >= tmhi) = 0;
end


