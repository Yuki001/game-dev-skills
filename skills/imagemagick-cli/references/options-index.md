# Complete command-line option index

Bundled ImageMagick 7 command-line option index with concise signatures and summaries. Search by exact option name. For detailed semantics and examples, consult the related task guide first, then this index.

## Alphabetical navigation

[A](#a) · [B](#b) · [C](#c) · [D](#d) · [E](#e) · [F](#f) · [G](#g) · [H](#h) · [I](#i) · [K](#k) · [L](#l) · [M](#m) · [N](#n) · [O](#o) · [P](#p) · [Q](#q) · [R](#r) · [S](#s) · [T](#t) · [U](#u) · [V](#v) · [W](#w)

## A

### -adaptive-blur radius [x sigma ]

Adaptively blur pixels, with decreasing effect near edges.

### -adaptive-resize geometry

Resize the image using data-dependent triangulation.

### -adaptive-sharpen radius [x sigma ]

Adaptively sharpen pixels, with increasing effect near edges.

### -adjoin

Join images into a single multi-image file.

### -affine s x , r x , r y , s y [, t x , t y ]

Set the drawing transformation matrix for combined rotating and scaling.

### -alpha type

Gives control of the alpha/matte channel of an image.

### -annotate degrees text

Annotate an image with text

### -antialias

Enable/Disable of the rendering of anti-aliasing pixels when drawing fonts and lines.

### -append

Join current images vertically or horizontally.

### -attenuate value

Lessen (or intensify) when adding noise to an image.

### -authenticate password

Decrypt a PDF with a password.

### -auto-gamma

Automagically adjust gamma level of image.

### -auto-level

Automagically adjust color levels of image.

### -auto-orient

Adjusts an image so that its orientation is suitable for viewing (i.e. top-left orientation).

### -auto-threshold method

Automatically perform image thresholding.

### -average

Average a set of images.

## B

### -backdrop

Display the image centered on a backdrop.

### -background color

Set the background color.

### -bench iterations

Measure performance.

### -bias value { % }

Add bias when convolving an image.

### -bilateral-blur width {x height }{ +intensity-sigma }{ +spatial-sigma }

A non-linear, edge-preserving, and noise-reducing smoothing filter for images. It replaces the intensity of each pixel with a weighted average of intensity values from nearby pixels. This weight is based on a Gaussian distribution. The weights depend not only on Euclidean distance of pixels, but also on the radiometric differences (e.g., range differences, such as color intensity, depth distance, etc.). This preserves sharp edges.

### -black-point-compensation

Use black point compensation.

### -black-threshold value { % }

Force to black all pixels below the threshold while leaving all pixels at or above the threshold unchanged.

### -blend geometry

Blend an image into another by the given absolute value or percent.

### -blue-primary x , y

Set the blue chromaticity primary point.

### -blue-shift factor

Simulate a scene at nighttime in the moonlight. Start with a factor of 1.5

### -blur radius -blur radius {x sigma }

Reduce image noise and reduce detail levels.

### -border geometry

Surround the image with a border of color.

### -bordercolor color

Set the border color.

### -borderwidth geometry

Set the border width.

### -brightness-contrast brightness -brightness-contrast brightness {x contrast }{ % }

Adjust the brightness and/or contrast of the image.

## C

### -cache threshold

(This option has been replaced by the -limit option).

### -canny radius -canny radius {x sigma }{ +lower-percent }{ +upper-percent }

Canny edge detector uses a multi-stage algorithm to detect a wide range of edges in the image.

### -caption string

Assign a caption to an image.

### -cdl filename

Color correct with a color decision list.

### -channel type

Specify those image color channels to which subsequent operators are limited.

### -channel-fx expression

Exchange, extract, or copy one or more image channels.

### -charcoal factor

Simulate a charcoal drawing.

### -chop geometry

Remove pixels from the interior of an image.

### -clahe width x height &#123%}{+} number-bins {+} clip-limit {!}

Contrast limited adaptive histogram equalization.

### -clamp

Set each pixel whose value is below zero to zero and any the pixel whose value is above the quantum range to the quantum range (e.g. 65535) otherwise the pixel value remains unchanged.

### -clip

Apply the clipping path if one is present.

### -clip-mask

Clip the image as defined by this mask.

### -clip-path id

Clip along a named path from the 8BIM profile.

### -clone index(s)

Make a clone of an image (or images).

### -clut

Replace the channel values in the first image using each corresponding channel in the second image as a c olor l ook u p t able.

### -coalesce

Fully define the look of each frame of a GIF animation sequence, to form a 'film strip' animation.

### -colorize value

Colorize the image by an amount specified by value using the color specified by the most recent -fill setting.

### -colormap type

Define the colormap type.

### -colors value

Set the preferred number of colors in the image.

### -color-matrix matrix

Apply color correction to the image.

### -colorspace value

Set the image colorspace.

### -color-threshold start-color - stop-color

Return a binary image where all colors within the specified range are changed to white. All other colors are changed to black.

### -combine

Combine one or more images into a single image.

### -comment string

Embed a comment in an image.

### -compare

Mathematically and visually annotate the difference between an image and its reconstruction

### -complex operator

Perform complex mathematics on an image sequence

### -compose operator

Set the type of image composition.

### -composite

Perform alpha composition on two images and an optional mask

### -compress type

Use pixel compression specified by type when writing the image.

### -connected-components connectivity

connected-components labeling detects connected regions in an image, choose from 4 or 8 way connectivity.

### -contrast

Enhance or reduce the image contrast.

### -contrast-stretch black-point -contrast-stretch black-point {x white-point }{ % }

Increase the contrast in an image by stretching the range of intensity values.

### -convolve kernel

Convolve an image with a user-supplied convolution kernel.

### -copy geometry offset

Copy pixels from one area of an image to another.

### -crop geometry { @ }{ ! }

Cut out one or more rectangular regions of the image.

### -cycle amount

Displace image colormap by amount.

## D

### -debug events

Enable debug printout.

### -decipher filename

Decipher and restore pixels that were previously transformed by -encipher .

### -deconstruct

Find areas that has changed between images

### -define key { =value } ...

Add specific global settings generally used to control coders and image processing operations.

### -delay ticks -delay ticks x ticks-per-second { < } { > }

Display the next image after pausing.

### -delete indexes

Delete the images specified by index, from the image sequence.

### -density width -density width x height

Set the horizontal and vertical resolution of an image for rendering to devices.

### -depth value

Depth of the image.

### -descend

Obtain image by descending window hierarchy.

### -deskew threshold&#123%}

Straighten an image. A threshold of 40% works for most images.

### -despeckle

Reduce the speckles within an image.

### -direction type

Render text right-to-left or left-to-right. Requires the RAQM delegate library and complex text layout .

### -displace horizontal-scale &#123%}{!} -displace horizontal-scale x vertical-scale &#123%}{!}

Shift image pixels as defined by a displacement map.

### -display host:display[.screen]

Specifies the X server to contact.

### -dispose method

Define the GIF disposal image setting for images that are being created or read in.

### -dissimilarity-threshold value

Maximum RMSE for subimage match (default 0.2).

### -dissolve src_percent [x dst_percent ]

Dissolve an image into another by the given percent.

### -distort method arguments

Distort an image, using the given method and its required arguments .

### -distribute-cache port

Launch a distributed pixel cache server.

### -dither method

Apply a Riemersma or Floyd-Steinberg error diffusion dither to images when general color reduction is applied via an option, or automagically when saving to specific formats. This enabled by default.

### -draw string

Annotate an image with one or more graphic primitives.

### -duplicate count,indexes

Duplicate an image one or more times.

## E

### -edge radius

Detect edges within an image.

### -emboss radius {x sigma

Emboss an image.

### -encipher filename

Encipher pixels for later deciphering by -decipher .

### -encoding type

Specify the text encoding.

### -endian type

Specify endianness ( MSB or LSB ) of the image.

### -enhance

Apply a digital filter to enhance a noisy image.

### -equalize

Perform histogram equalization on the image channel-by-channel.

### -evaluate operator value

Alter channel pixels by evaluating an arithmetic, relational, or logical expression.

### -evaluate-sequence operator

Alter channel pixels by evaluating an arithmetic, relational, or logical expression over a sequence of images. Ensure all the images in the sequence are in the same colorspace, otherwise you may get unexpected results, e.g. add -colorspace sRGB to your command-line.

### -exit

Stop processing at this point.

### -extent geometry

Set the image size and offset.

### -extract geometry

Extract the specified area from image.

## F

### -family fontFamily

Set a font family for text.

### -features distance

Display (co-occurrence matrix) texture measure features for each channel in the image in each of four directions (horizontal, vertical, left and right diagonals) for the specified distance.

### -fft

Implements the forward discrete Fourier transform (DFT).

### -fill color

Color to use when filling a graphic primitive.

### -filter type

Use this type of filter when resizing or distorting an image.

### -flatten

This is a simple alias for the -layers method "flatten".

### -flip

Create a mirror image

### -floodfill { +- } x { +- } y color

Floodfill the image with color at the specified offset.

### -flop

Create a mirror image .

### -font name

Set the font to use when annotating images with text, or creating labels.

### -foreground color

Define the foreground color for menus.", "display

### -format type

The image format type.

### -format expression

Output formatted image characteristics.

### -frame geometry

Surround the image with a border or beveled frame.

### -frame

Include the X window frame in the imported image.

### -function function parameters

Apply a function to channel values.

### -fuzz distance { % }

Colors within this distance are considered equal.

### -fx expression

Apply a mathematical expression to an image or image channels.

## G

### -gamma value

Level of gamma correction.

### -gaussian-blur radius -gaussian-blur radius {x sigma }

Blur the image with a Gaussian operator.

### -geometry geometry

Set the preferred size and location of the image.

### -gravity type

Sets the current gravity suggestion for various other settings and options.

### -grayscale method

Convert image to grayscale.

### -green-primary x,y

Green chromaticity primary point.

## H

### -hald-clut

Apply a Hald color lookup table to the image.

### -help

Print usage instructions.

### -highlight-color color

When comparing images, emphasize pixel differences with this color.

### -hough-lines width x height { +threshold }

Identify straight lines in the image (e.g. -hough-lines 9x9+195).

## I

### -iconGeometry geometry

Specify the icon geometry.

### -iconic

Start in icon mode in X Windows", 'animate', 'display

### -identify

Identify the format and characteristics of the image.

### -ift

Implements the inverse discrete Fourier transform (DFT).

### -illuminant method

reference illuminant. Choose from A , B , C , D50 , D55 , D65 , E , F2 , F7 , or F11 .

### -immutable

Make image immutable.

### -implode factor

Implode image pixels about the center.

### -insert index

Insert the last image into the image sequence.

### -intensity method

Method to generate intensity value from pixel.

### -intent type

Use this type of rendering intent when managing the image color.

### -interlace type

The type of interlacing scheme.

### -interline-spacing value

The space between two text lines.

### -interpolate type

Set the pixel color interpolation method to use when looking up a color based on a floating point or real value.

### -interpolative-resize geometry

Resize with interpolation. See the -interpolate setting.

### -interword-spacing value

The space between two words.

### -integral

Calculate the sum of values (pixel values) in the image.

## K

### -kerning value

The space between two letters.

### -kmeans colors {x iterations }{+ tolerance }

Kmeans (iterative) color reduction (e.g. -kmeans 5x300+0.0001 ). Colors is the desired number of colors. Initial colors are found using color quantization. Iterations is the stopping number of iterations (default=300). Convergence is the stopping threshold on the color change between iterations (default=0.0001). Processing finishes, if either iterations or tolerance are reached. Use -define kmeans:seed-colors= color-list to initialize the colors, where color-list is a semicolon delimited list of seed colors (e.g. -define kmeans:seed-colors="red;sRGB(19,167,254);#00ffff ). A color list overrides the color quantization. A non-empty list of colors overrides the number of colors. Any unassigned initial colors are assigned random colors from the image.

### -kuwahara radius -kuwahara radius {x sigma }

Edge preserving noise reduction filter.

## L

### -label name

Assign a label to an image.

### -lat width -lat width x height { +- } offset { % }

Perform local adaptive threshold.

### -layers method

Handle multiple images forming a set of image layers or animation frames.

### -lat width x height {+-} offset {%}

Perform local adaptive thresholding.

Compatibility note: use current `-lat` rather than the historical `-adaptive-threshold` spelling.

### -level black_point {, white_point }{ % }{, gamma }

Adjust the level of image channels.

### -level-colors { black_color }{,}{ white_color }

Adjust the level of an image using the provided dash separated colors.

### -limit type value

Set the pixel cache resource limit.

### -linear-stretch black-point -linear-stretch black-point {x white-point }{ % }

Linear with saturation stretch.

### -linewidth

The line width for subsequent draw operations.

### -liquid-rescale geometry

Rescale image with seam-carving.

### -list type

Print a list of supported arguments for various options or settings. Choose from these list types:

### -log string

Specify format for debug log.

### -loop iterations

Add Netscape loop extension to your GIF animation.

### -lowlight-color color

When comparing images, de-emphasize pixel differences with this color.

## M

### -magnify

Double or triple the size of the image with pixel art scaling. Specify an alternative scaling method with -define magnify:method= method Choose from these methods: eagle2X, eagle3X, eagle3XB, epb2X, fish2X, hq2X, scale2X, scale3X, xbr2X . The default is scale2X.

### -map type

Display image using this type .

### -map components

Pixel map.

### -mattecolor color

Specify the color to be used with the -frame option.

### -maximum

Return the maximum intensity of an image sequence.

### -median geometry

Apply a median filter to the image.

### -mean-shift width x height { +distance &#123%}

Image noise removal and color reduction/segmentation (e.g. -mean-shift 7x7+10%).

### -metric type

Output to STDERR a measure of the differences between images according to the type given metric.

### -minimum

Return the minimum intensity of an image sequence.

### -mode geometry

Make each pixel the \'predominant color\' of the neighborhood.'

### -modulate brightness [, saturation , hue ]

Vary the brightness , saturation , and hue of an image.

### -moments

Report image moments and perceptual hash.

### -monitor

Monitor progress.

### -monochrome

Transform the image to black and white.

### -morph frames

Morphs an image sequence.

### -morphology

Apply a morphology method to the image.

### -mosaic

A simple alias for the -layers method "mosaic"

### -motion-blur radius -motion-blur radius {x sigma }+ angle

Simulate motion blur.

## N

### -name

Name an image.

### -negate

Replace each pixel with its complementary color.

### -noise geometry +noise type

Add or reduce noise in an image.

### -normalize

Increase the contrast in an image by stretching the range of intensity values.

## O

### -opaque color

Change this color to the fill color within the image.

### -ordered-dither threshold_map {, level ...}

Dither the image using a pre-defined ordered dither threshold map specified, and a uniform color map with the given number of levels per color channel.

### -orient image orientation

Specify orientation of a digital camera image.

## P

### -page geometry -page media [ offset ][{ ^!<> }] +page

Set the size and location of an image on the larger virtual canvas.

### -paint radius

Simulate an oil painting.

### -path path

Write images to this path on disk.

### -pause seconds

Pause between animation loops

### -pause seconds

Pause between snapshots.

### -perceptible epsilon

Set each pixel whose value is less than | epsilon | to -epsilon or epsilon (whichever is closer) otherwise the pixel value remains unchanged.

### -ping

Efficiently determine these image characteristics: image number, the file name, the width and height of the image, whether the image is colormapped or not, the number of colors in the image, the number of bytes in the image, the format of the image (JPEG, PNM, etc.). Use +ping to ensure accurate image properties.

### -pointsize value

Pointsize of the PostScript, X11, or TrueType font.

### -polaroid angle

Simulate a Polaroid picture.

### -poly "wt,exp ..."

Combines multiple images according to a weighted sum of polynomials; one floating point weight (coefficient) and one floating point polynomial exponent (power) for each image expressed as comma separated pairs.

### -posterize levels

Reduce the image to a limited number of color levels per channel.

### -precision value

Set the maximum number of significant digits to be printed.

### -preview type

Image preview type.

### -print string

Interpret string and print to console.

### -process command

Process the image with a custom image filter.

### -profile filename +profile profile_name

Manage ICM, IPTC, or generic profiles in an image.

## Q

### -quality value

control the compression quality of JPEG, PNG, HEIC, and WebP image files when you are creating or saving them. This option is important for managing the trade-off between image quality and file size.

### -quantize colorspace

Reduce colors using this colorspace.

### -quiet

Suppress all warning messages. Error messages are still reported.

## R

### -raise thickness

Lighten or darken image edges.

### -random-threshold low x high

Apply a random threshold to the image.

### -range-threshold low-black , low-white , high-white , high-black

Perform either hard or soft thresholding within some range of values in an image.

### -read filename

Explicit read of an image rather than an implicit read.

### -read-mask filename

Prevent updates to image pixels specified by the mask.

### -red-primary x,y

Set the red chromaticity primary point.

### -regard-warnings

Pay attention to warning messages.

### -remap filename

Reduce the number of colors in an image to the colors used by this image.

### -region geometry

Set a region in which subsequent operations apply.

### -remote

Perform a remote operation.

### -render

Render vector operations.

### -repage geometry

Adjust the canvas and offset information of the image.

### -resample horizontal x vertical

Resample image to specified horizontal and vertical resolution.

### -reshape geometry

Reshape an image.

### -resize geometry

Resize an image.

### -respect-parentheses

Settings remain in effect until parenthesis boundary.

### -reverse

Reverse the order of images in the current image list.

### -roll { +- } x { +- } y

Roll an image vertically or horizontally by the amount given.

### -rotate degrees { < }{ > }

Apply Paeth image rotation (using shear operations) to the image.

### -rotational-blur angle

Blur around the center of the image.

## S

### -sample geometry

Minify / magnify the image with pixel subsampling and pixel replication, respectively.

### -sampling-factor horizontal-factor x vertical-factor

Sampling factors used by JPEG or MPEG-2 encoder and YUV decoder/encoder.

### -scale geometry

Minify / magnify the image with pixel block averaging and pixel replication, respectively.

### -scene value

Set scene number.

### -screen

Specify the screen to capture.

### -script filename

Transfer control to the named file.

### -seed

Seed a new sequence of pseudo-random numbers

### -segment cluster-threshold x smoothing-threshold

Segment the colors of an image.

### -selective-blur radius -selective-blur radius {x sigma }{ +threshold }

Selectively blur pixels within a contrast threshold.

### -separate

Separate an image channel into a grayscale image. Specify the channel with -channel .

### -sepia-tone percent-threshold

Simulate a sepia-toned photo.

### -set key value

Sets image attributes and properties for images in the current image sequence.

### -shade azimuth x elevation

Shade the image using a distant light source.

### -shadow percent-opacity {x sigma }{ +- } x { +- } y { % }

Simulate an image shadow.

### -sharpen radius -sharpen radius {x sigma }

Sharpen the image.

### -shave geometry

Shave pixels from the image edges.

### -shear Xdegrees [x Ydegrees ]

Shear the image along the x-axis and/or y-axis.

### -sigmoidal-contrast contrast x mid-point

Increase the contrast without saturating highlights or shadows.

### -silent

Operate silently. This option is only used by the import tool.

### -similarity-threshold value

Minimum RMSE for subimage match.

### -size width [x height ][ +offset ]

Set the width and height of the image.

### -sketch radius -sketch radius {x sigma }+ angle

Simulate a pencil sketch.

### -smush offset

Appends an image sequence together ignoring transparency.

### -snaps value

Set the number of screen snapshots.

### -solarize percent-threshold

Negate all pixels above the threshold level.

### -sort-pixels

sorts pixels within each scanline in ascending order of intensity.

### -sparse-color method ' x , y color ...'

color the given image using the specified points of color, and filling the other intervening colors using the given methods.

### -splice geometry

Splice the current background color into the image.

### -spread amount

Displace image pixels by a random amount.

### -statistic type geometry

Replace each pixel with corresponding statistic from the neighborhood.

### -stegano offset

Hide watermark within an image.

### -stereo +x { +y }

Composite two images to create a red / cyan stereo anaglyph.

### -storage-type type

Pixel storage type. Here are the valid types:

### -stretch fontStretch

Set a type of stretch style for fonts.

### -strip

Strip the image of any profiles, comments or these PNG chunks: bKGD,cHRM,EXIF,gAMA,iCCP,iTXt,sRGB,tEXt,zCCP,zTXt,date. To remove the orientation chunk, orNT , set the orientation to undefined, e.g., -orient Undefined .

### -stroke color

Color to use when stroking a graphic primitive.

### -strokewidth value

Set the stroke width.

### -style fontStyle

Set a font style for text.

### -subimage-search

Search for subimage.

### -swap index,index

Swap the positions of two images in the image sequence.

### -swirl degrees

Swirl image pixels about the center.

### -synchronize

Synchronize image to storage device.

## T

### -taint

Mark the image as modified.

### -text-font name

Font for writing fixed-width text.

### -texture filename

Name of texture to tile onto the image background.

### -threshold value { % }

Apply simultaneous black/white threshold to the image.

### -thumbnail geometry

Create a thumbnail of the image.

### -tile filename

Set the tile image used for filling a subsequent graphic primitive.

### -tile-offset { +- } x { +- } y

Specify the offset for tile images, relative to the background image it is tiled on.

### -tint value

Tint the image with the fill color.

### -title string

Assign a title to displayed image.", "animate", "display", "montage

### -transform

Transform the image.

### -transparent color

Make this color transparent within the image.

### -transparent-color color

Set the transparent color.

### -transpose

Mirror the image along the top-left to bottom-right diagonal.

### -transverse

Mirror the image along the images bottom-left top-right diagonal. Equivalent to the operations -flop -rotate 90 .

### -treedepth value

Tree depth for the color reduction algorithm.

### -trim

Trim an image.

### -type type

The image type.

## U

### -undercolor color

Set the color of the annotation bounding box.

### -update seconds

Detect when image file is modified and redisplay.

### -unique-colors

Discard all but one of any pixel color.

### -units type

The units of image resolution.

### -unsharp radius -unsharp radius {x sigma }{ +gain }{ +threshold }

Sharpen the image with an unsharp mask operator.

## V

### -verbose

Print detailed information about the image when this option precedes the -identify option or info: .

### -version

Print ImageMagick version string and exit.

### -view string

FlashPix viewing parameters.

### -vignette radius {x sigma }{ +- } x { +- } y { % }

Soften the edges of the image in vignette style.

### -virtual-pixel method

Specify contents of virtual pixels .

### -visual type

Animate images using this X visual type.", 'animate', 'display'

## W

### -watermark brightness x saturation

Watermark an image using the given percentages of brightness and saturation.

### -wave amplitude -wave amplitude x wavelength

Shear the columns of an image into a sine wave.

### -wavelet-denoise threshold -wavelet-denoise threshold x softness

Removes noise from the image using a wavelet transform. The threshold is the value below which everything is considered noise and ranges from 0.0 (none) to QuantumRange or use percent (e.g. 5%). Softness attenuates the threshold and typically ranges from 0.0 (none, default) to 1.0. The higher the value, the more noise that remains in the image.

### -weight fontWeight

Set a font weight for text.

### -white-balance

Applies white balancing to an image according to a grayworld assumption in the LAB colorspace.

### -white-point x,y

Chromaticity white point.

### -white-threshold value { % }

Force to white all pixels above the threshold while leaving all pixels at or below the threshold unchanged.

### -window id

Make the image the background of a window.", 'animate', 'display'

### -window-group

Specify the window group.

### -word-break type

Sets whether line breaks appear wherever the text would otherwise overflow its content box. Choose from normal , the default, or break-word .

### -write filename

Write an image sequence.

### -write-mask filename

Prevent updates to image pixels specified by the mask.

