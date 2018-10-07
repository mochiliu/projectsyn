%% generate random colors prompt text input, save
image_width = 100;
if ~exist('color_descriptions','var')
    color_descriptions = [];
end
while true
    color = randi(255,1,3)./255;

    color_image = repmat(color, image_width*image_width, 1);
    color_image = reshape(color_image, image_width, image_width, 3);
    imshow(color_image)

    description = input('describe this color: ','s');
    if strcmp(description, 'exit')
        break
    else
        data_count = length(color_descriptions) + 1;
        color_descriptions(data_count).color = color;
        color_descriptions(data_count).description = description;
    end
end

%% allow user to generate color pickings directly 
image_width = 100;
if ~exist('color_descriptions','var')
    color_descriptions = [];
end
fig = openfig('Choose_Color.fig')
word = input('word: ','s');
while true
    description = input('type exit to stop: ','s');
    if strcmp(description, 'exit')
        break
    else
        data_count = length(color_descriptions) + 1;
        color_descriptions(data_count).color = kleur;
        color_descriptions(data_count).description = word;
    end    
end


%% each word gets its own data points
list_of_words = [];
points_in_colorspace = [];

for data_index = 1:length(color_descriptions)
   current_words = strsplit(color_descriptions(data_index).description, ' ');
   for word_index = 1:length(current_words)
      current_word = current_words{word_index};
       idx = find(ismember(list_of_words, current_word));
       if ~isempty(idx)
          % word already exists
          points_in_colorspace{idx} = [points_in_colorspace{idx}; color_descriptions(data_index).color];
       else
           idx = length(list_of_words) + 1;
           list_of_words{idx} = current_word;
           points_in_colorspace{idx} = color_descriptions(data_index).color;
       end
   end
end

%% plot the cloud of the color points for word
for word_index = 1:1
    word = list_of_words{word_index};
    word_points = points_in_colorspace{word_index};
    scatter3(word_points(:,1),word_points(:,2),word_points(:,3));
    axis([0 1 0 1 0 1])
end

%% construct pdfs in color space for each word, using dim example
