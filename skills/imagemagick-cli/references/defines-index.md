# Complete `-define` key index

Bundled `-define` key reference. Availability depends on the installed coder, delegate, and ImageMagick version. Place read-related defines before the input they affect.

## Prefix navigation

[{caption,label}](#captionlabel) · [ashlar](#ashlar) · [auto-threshold](#auto-threshold) · [bmp](#bmp) · [bmp3](#bmp3) · [caption](#caption) · [color](#color) · [colorspace](#colorspace)

[compare](#compare) · [complex](#complex) · [compose](#compose) · [connected-components](#connected-components) · [convolve](#convolve) · [dcm](#dcm) · [dds](#dds) · [delegate](#delegate)

[deskew](#deskew) · [distort](#distort) · [dither](#dither) · [dng](#dng) · [dot](#dot) · [eps](#eps) · [exif](#exif) · [exr](#exr)

[filename](#filename) · [filter](#filter) · [fourier](#fourier) · [fpx](#fpx) · [frames](#frames) · [ftxt](#ftxt) · [fx](#fx) · [general](#general)

[gradient](#gradient) · [h](#h) · [heic](#heic) · [histogram](#histogram) · [hough-lines](#hough-lines) · [icon](#icon) · [identify](#identify) · [image](#image)

[jp2](#jp2) · [jpeg](#jpeg) · [json](#json) · [jxl](#jxl) · [kmeans](#kmeans) · [magick](#magick) · [magnify](#magnify) · [minimum-bounding-box](#minimum-bounding-box)

[mng](#mng) · [modulate](#modulate) · [morphology](#morphology) · [pango](#pango) · [pcl](#pcl) · [pdf](#pdf) · [phash](#phash) · [pixel](#pixel)

[png](#png) · [precision](#precision) · [profile](#profile) · [ps](#ps) · [psd](#psd) · [ptif](#ptif) · [quantum](#quantum) · [registry](#registry)

[resample](#resample) · [sample](#sample) · [shepards](#shepards) · [stream](#stream) · [svg](#svg) · [tga](#tga) · [tiff](#tiff) · [trim](#trim)

[txt](#txt) · [type](#type) · [uhdr](#uhdr) · [video](#video) · [webp](#webp) · [white-balance](#white-balance) · [x](#x) · [xmp](#xmp)

## {caption,label}

### `{caption,label}:{max,start}-pointsize= value`

This sets the bounding pointsize to use when searching for the maximum pointsize where the text annotation still fits within the image boundaries.

## ashlar

### `ashlar:best-fit`

align tiles on both the left and right edges.

### `ashlar:tiles`

set the maximum number of image tiles to render per canvas.

## auto-threshold

### `auto-threshold:verbose`

return derived threshold as the auto-threshold:threshold image property.

## bmp

### `bmp:format= value`

Valid values are bmp2 , bmp3 , and bmp4 . This option can be useful when the method of prepending "BMP2:" to the output filename is inconvenient or is not available, such as when using the mogrify utility.

### `bmp:subtype= value`

BMP channel depth subtypes. The choices are: RGB555, RGB565, ARGB4444, ARGB1555. Only support in BMP (BMP4). BMP3 and BMP2 do not contain header fields to support these options.

## bmp3

### `bmp3:alpha= true|false`

Include any alpha channel when writing in the BMP image format.

## caption

### `caption:max-pointsize= pointsize`

Limit the maximum point size

### `caption:split= boolean`

split text if required to fit caption on canvas

## color

### `color:illuminant`

reference illuminant, defaults to D65.

## colorspace

### `colorspace:auto-grayscale= on|off`

Prevent automatic conversion to grayscale inside coders that support grayscale. This should be accompanied by -type truecolor. PNG and TIF do not need this define. With PNG, just use PNG24:image. With TIF, just use -type truecolor. JPG and PSD will need this define.

## compare

### `compare:frequency-domain= boolean`

Certain similarity metrics such as DPC, MSE, NCC, PSNR, Phase, and RMSE operate in the frequency domain when FFTW and HDRI are enabled. To utilize their spatial equivalents, you can use the command -define compare:frequency-domain=false . However, note that DPC and PHASE metrics do not have spatial equivalents, so this command will be ignored for them.

### `compare:ssim-radius= value`

Set the structural similarity index radius.

### `compare:ssim-sigma= value`

Set the structural similarity index sigma.

### `compare:ssim-k1= value`

Set the structural similarity index k1 argument.

### `compare:ssim-k2= value`

Set the structural similarity index k2 argument.

### `compare:virtual-pixels= boolean`

ImageMagick compares images pixel by pixel, aligning from the top-left corner. If sizes differ, unmatched areas in the smaller image are treated as virtual pixels, possibly affecting comparison results. To limit comparison to authentic pixels only, use -define compare:virtual-pixels=false .

## complex

### `complex:snr= value`

Set the divide SNR constant -complex .

## compose

### `compose:args= arguments`

Set certain compose argument values when using convert ... -compose ... -composite. See Image Composition .

### `compose:clip-to-self= true|false`

Some -compose methods can modify the 'destination' image outside the overlay area. It is disabled by default.

### `compose:clamp= on|off`

Set each pixel whose value is below zero to zero and any the pixel whose value is above the quantum range to the quantum range (e.g. 65535) otherwise the pixel value remains unchanged. Define supported in ImageMagick 6.9.1-3 and above.

### `compose:colorspace= colorspace`

Set the colorspace for the colorize composite operator. The default is HCL.

### `compose:compose= on|off`

This special usage allows you to perform true mathematics of the image channels, without alpha composition effects, becoming involved.

## connected-components

### `connected-components:angle-threshold= value`

Merges any region with equivalent ellipse angle smaller than value into its surrounding region or largest neighbor. Supported in Imagemagick 7.0.9.24.

### `connected-components:area-threshold= value`

Merges any region with area smaller than value into its surrounding region or largest neighbor. Thresholds can optionally include ranges, e.g. 410-1600.

### `connected-components:background-id= object-id`

Identify which object is to be the background object. Supported in Imagemagick 7.0.9.21.

### `connected-components:circularity-threshold= value`

Merge any region with circularity smaller than value into its surrounding region or largest neighbor. Circularity is computed as 4*pi*area/perimeter^2. Supported in Imagemagick 7.0.9.24.

### `connected-components:diameter-threshold= value`

Merge any region with diameter smaller than value into its surrounding region or largest neighbor. Diameter is computed as sqrt(4*area/pi). Supported in Imagemagick 7.0.9.24.

### `connected-components:eccentricity-threshold= value`

Merge any region with equivalent ellipse eccentricity smaller than value into its surrounding region or largest neighbor. Supported in Imagemagick 7.0.9.24.

### `connected-components:exclude-header= true`

List the objects without the header. Supported in Imagemagick 7.0.9.21.

### `connected-components:keep= list-of-ids`

Comma and/or hyphenated list of id values to keep in the output. Supported in Imagemagick 6.9.3-0.

### `connected-components:keep-colors= red;green;blue`

Keeps objects identified by their color in a semicolon separated list. Supported in Imagemagick 6.9.3-0.

### `connected-components:keep-top= number-of-objects`

Keeps only the top number of objects by area. Supported in Imagemagick 7.0.9.21.

### `connected-components:major-axis-threshold= value`

Merge any region with equivalent ellipse major axis diameter smaller than value into its surrounding region or largest neighbor. Supported in Imagemagick 7.0.9.24.

### `connected-components:mean-color= true`

Change the output image from id values to mean color values. Supported in Imagemagick 6.9.2-8.

### `connected-components:minor-axis-threshold= value`

Merge any region with equivalent ellipse minor axis diameter smaller than value into its surrounding region or largest neighbor. Supported in Imagemagick 7.0.9.24.

### `connected-components:perimeter-threshold= value`

Merge any region with perimeter smaller than value into its surrounding region or largest neighbor. Supported in Imagemagick 7.0.9.24.

### `connected-components:remove= list-of-ids`

Comma and/or hyphenated list of id values to remove from the output. Supported in Imagemagick 6.9.2-9.

### `connected-components:remove-colors= red;green;blue`

Remove objects identified by their color in a semicolon separated list. Supported in Imagemagick 6.9.3-0.

### `connected-components:verbose= true`

Lists id, bounding box, centroid, area, mean color for each region.

## convolve

### `convolve:scale= {kernel_scale}[!^] [,{origin_addition}] [%]`

Define the kernel scaling. The special flag ! automatically scales to full dynamic range. The ! flag can be used in combination with a factor or percent. The factor or percent is then applied after the automatic scaling. An example is 50%!. This produces a result 50% darker than full dynamic range scaling. The ^ flag assures the kernel is 'zero-summing', for example when some values are positive and some are negative as in edge detection kernels. The origin addition adds that value to the center pixel of the kernel. This produces an effect that is like adding the image that many times to the result of the filtered image. The typical value is 1 so that the original image is added to the result of the convolution. The default is 0.

## dcm

### `dcm:display-range= reset`

Set the display range to the minimum and maximum pixel values for the DCM image format.

### `dcm:fix-byte-order= true`

Fix incorrect byte order when reading pixels from the file.

### `dcm:rescale= true`

Enable interpretation of the rescale slope and intercept settings in the file.

### `dcm:rescale= true`

Enable interpretation of the rescale slope and intercept settings in the file.

### `dcm:window= CxW`

Specify the dcm window center and width.

## dds

### `dds:cluster-fit= true|false`

Enable the DDS cluster-fit.

### `dds:compression= dxt1|dxt5|none`

Set the dds compression.

### `dds:mipmaps= value`

Set the dds number of mipmaps.

### `dds:weight-by-alpha= true|false`

Enable the DDS alpha weighting.

## delegate

### `delegate:bimodal= true`

Specify direct conversion from Postscript to PDF.

## deskew

### `deskew:auto-crop= true`

auto crop the image after deskewing.

## distort

### `distort:scale= value`

Set the output scaling factor for use with -distort .

### `distort:viewport= WxH+X+Y`

Set the viewport for use with -distort .

## dither

### `dither:diffusion-amount= X%`

Set the amount of diffusion to use with Floyd-Steinberg diffusion

## dng

### `dng:max-raw-memory= value`

Stop processing if raw buffer size grows larger than that value (in megabytes). Default is 8192.

### `dng:no-auto-bright= true`

Disable the histogram-based white level.

### `dng:output-color= value`

Select the output colorspace. The choices are: 0 - Raw color (unique to each camera), 1 - sRGB D65 (default), 2 - Adobe RGB (1998) D65, 3 - Wide Gamut RGB D65, 4 - Kodak ProPhoto RGB D65, 5 - XYZ, 6 - ACES

### `dng:read-thumbnail= true`

Read the embedded thumbnail and store it as a profile called 'dng:thumbnail'.

### `dng:use-auto-wb= true`

Compute the white balance by averaging the entire image.

### `dng:use-camera-wb= true`

Uses the white balance specified by the camera. Default is true.

## dot

### `dot:layout-engine= value`

Specify the layout engine for the DOT image format (e.g., neato ).

## eps

### `eps:use-cropbox= true`

Force Imagemagick to respect the crop box.

## exif

### `exif:sync-image=false`

By default, the resolution of the image is synced with the EXIF profile. Use this define to ignore the EXIF profile.

## exr

### `exr:color-type= value`

Specify the color type for the EXR format: RGB, RGBA, YC, YCA, Y, YA, R, G, B, A).

## filename

### `filename:literal= true`

By default, output filenames can contain embedded formatting characters . Use this option to bypass interpreting embedded formatting characters and instead use the filename literally.

## filter

### `filter:option= value`

Set a filter option for use with -resize . See below for specific options.

### `filter:b= value`

Redefine the spline factor used for cubic filters such as Cubic, Catrom, Mitchel, and Hermite, as well as the Parzen cubic windowing function. If only one of the b or c values are defined, the other is set so as to generate a 'Cubic-Keys' filter. The meaning of the b and c values was defined in a research paper by Mitchell-Netravali.

### `filter:blur= factor`

Scale the X axis of the filter (and its window). Use > 1.0 for blurry or < 1.0 for sharp. This should only be used with Gaussian and Gaussian-like filters simple filters, or you may not get the expected results.

### `filter:c= value`

Redefine the Keys alpha factor used for cubic filters such as Cubic, Catrom, Mitchel, and Hermite, as well as the Parzen cubic windowing function. If only one of the b or c values are defined, the other is set so as to generate a 'Cubic-Keys' filter. The meaning of the b and c values was defined in a research paper by Mitchell-Netravali.

### `filter:kaiser-alpha= value`

Set the Kaiser window alpha value. When it is multiplied by 'PI', it is equivalent to "kaiser-beta" and will override that setting. It only affects the Kaiser windowing function and does not affect any other attributes.

### `filter:kaiser-beta= value`

Set the Kaiser window beta value. It only affects Kaiser windowing function and does not affect any other attributes. Before ImageMagick v6.7.6-10, this option was known as "filter:alpha" (an inheritance from the very old "zoom" program). It was changed to bring the function in line with more modern academic research usage and better assign it be more definitive. The default value is 6.5

### `filter:lobes= count`

Set the number of lobes to use for the Sinc/Bessel filter. This is an alternate way of specifying the 'support' range of the filter, that is designed to be more suited to windowed filters, especially when used for image distorts.

### `filter:sigma= value`

Set the 'sigma' value used to define the Gaussian filter. The default sigma value is '0.5'. It only affects the Gaussian filter, but does not shrink (but may enlarge) the filter's 'support'. It can be used to generate very small blurs, but without the filter 'missing' pixels due to using a small support setting. A larger value of '0.707' (a value of '1/sqrt(2)') is another common setting.

### `filter:support= radius`

Set the filter support radius. It defines how large the filter should be and thus directly defines how slow the filtered resampling process is. All filters have a default 'preferred' support size. Some filters like Lagrange and windowed filters adjust themselves depending on this value. With simple filters this value either does nothing (but slow the resampling), or will clip the filter function in a detrimental way.

### `filter:verbose= true`

Enable printing of information about the final internal filter selection to standard output. This includes a commented header on the filter settings being used and data allowing the filter weights to be easily graphed. Note however that some filters are internally defined in terms of other filters. The Lanczos filter, for example, is defined in terms of a SincFast windowed SincFast filter, while the Mitchell filter is defined as a general Cubic family filter with specific 'B' and 'C' settings.

### `filter:window= filter_function`

The IIR (infinite impulse response) filters Sinc and Jinc are windowed (brought down to zero over the defined support range) with the given filter. This allows you to specify a filter function to be used as a windowing function for these IIR filters. Many of the defined filters are actually windowing functions for these IIR filters. A typical choices is Box, (which effectively turns off the windowing function).

### `filter:window-support= radius`

Scale the windowing function to this size. This causes the windowing (or self-windowing Lagrange filter) to act is if the support window is larger than what is actually supplied to the calling operator. The filter, however, is still clipped to the true support size that is provided. If unset, this will equal the normal filter support size.

## fourier

### `fourier:normalize= inverse`

Set the location for the FFT/IFT normalization as use by +-fft and +-ift . The default is forward .

## fpx

### `fpx:view= value`

Specify the FlashPix viewing object, which contains the specification of a viewing transform. The viewing transform enables applications to represent a set of simple edits as a list of "commands" which are applied to the image in real time without altering the original image.

## frames

### `frames:step`

When selecting image frames , the default is to step one frame at a time through a list, e.g. [0-3], returns frames 0, 1, 2, and 3. Set the step to 2 in this example and we instead get frames 0 and 2.

## ftxt

### `ftxt:chsep= value`

A single text character that separates channel values for reading and writing. Default: "," (Comma).

### `ftxt:format= value`

The format string for writing and reading. Default: "\x,\y:\c". For escapes \x etc, see [ftxt: formatted text](http://im.snibgo.com/fmttxt.htm).

### `ftxt:hasalpha= value`

Whether the text has an alpha channel, for reading only. Default: false.

### `ftxt:nummeta= value`

The number of meta channels, for reading only. Default 0 (Zero).

## fx

### `fx:debug=true`

Debug -fx expression.

## general

### `preserve-timestamp= true|false`

Preserve file timestamp ( mogrify only).

### `q-table= quantization-table.xml`

Custom JPEG quantization tables.

## gradient

### `gradient:angle= angle (in degrees)`

For a linear gradient, this specifies the direction of the gradient going from color1 to color2 in a clockwise positive manner relative to north (up). For a radial gradient, this specifies the rotation of the gradient in a clockwise positive manner from its normal X-Y orientation. Supported in Imagemagick 6.9.2-5.

### `gradient:bounding-box= WxH+X+Y`

Limit the gradient to a larger or smaller region than the image dimensions. If the region defined by the bounding box is smaller than the image, then color1 will be the color of the background. Supported in Imagemagick 6.9.2-5.

### `gradient:center= x,y`

Specify the coordinates of the center point for the radial gradient. The default is the center of the image. Supported in Imagemagick 6.9.2-5.

### `gradient:direction= value`

Specify the direction of the linear gradient towards the top/bottom/left/right or diagonal corners. The choices are: NorthWest, North, Northeast, West, East, SouthWest, South, SouthEast. Supported in Imagemagick 6.9.2-5.

### `gradient:extent= value`

Specify the shape of an image centered radial gradient. The choices are: Circle, Diagonal, Ellipse, Maximum, Minimum. Circle and Maximum draw a circular radial gradient even for rectangular shaped images of radius equal to the larger of the half-width and half-height of the image. The Circle and Maximum options are both equivalent to the default radial gradient. The Minimum option draws a circular radial gradient even for rectangular shaped images of radius equal to the smaller of the half-width and half-height of the image. The Diagonal option draws a circular radial gradient even for rectangular shaped images of radius equal to the half-diagonal of the image. The Ellipse options draws an elliptical radial gradient for rectangular shaped images of radii equal to half the width and half the height of the image. Supported in Imagemagick 6.9.2-5.

### `gradient:radii= x,y`

Specify the x and y radii of the gradient. If the x radius and the y radius are equal, the shape of the radial gradient will be a circle. If they differ, then the shape will be an ellipse. The default values are the maximum of the half width and half height of the image. Supported in Imagemagick 6.9.2-5.

### `gradient:vector= x1,y1,x2,y2`

Specify the direction of the linear gradient going from vector1 (x1,y1) to vector2 (x2,y2). Color1 (fromColor) will be located at vector position x1,y1 and color2 (toColor) will be located at vector position x2,y2. Supported in Imagemagick 6.9.2-5.

## h

### `h:format= value`

Set the image encoding format use when writing a C-style header. format can be any output format supported by ImageMagick except for h and magick . If this option is omitted, the default is GIF for PseudoClass images and PNM for DirectClass images.

## heic

### `heic:chroma= value`

Set the HEIC chroma parameter. Possible values are: "420", "422", "444". Default is "420"", except output with preserved CICP matrix coefficient 0 uses "444" when this define is omitted because identity matrix CICP cannot be written with chroma subsampling.

### `heic:cicp= value`

Set the HEIC color primaries, transfer characteristics, matrix coefficients, and full range flag. Use 1/13/6/1 for full range BT.709. If omitted, the source HEIC CICP value is preserved when available unless heic:preserve-cicp=false is set. When preserving source matrix coefficient 0 with heic:chroma=420 or 422 , ImageMagick writes matrix coefficient 6 (BT.601) for the subsampled YCbCr output. Explicit heic:cicp values with matrix coefficient 0 require heic:chroma=444 . See ISO/IEC 14496-12:2022 standard for a description of these fields and values.

### `heic:clli= value`

Set the HEIC content light level information as MaxCLL,MaxFALL . If omitted, the source HEIC content light level is preserved when available unless heic:preserve-clli=false is set.

### `heic:depth-image= true`

Extract the depth image if the container has one.

### `heic:max-number-of-tiles= value`

Sets the maximum number of tiles of a HEIC image.

### `heic:max-bayer-pattern-pixels= value`

Sets the maximum bayer pattern size in pixels of a HEIC image.

### `heic:max-items= value`

Sets the maximum number of items in a box of a HEIC image.

### `heic:max-components= value`

Sets the maximum number of components of a HEIC image.

### `heic:max-iloc-extents-per-item= value`

Sets the maximum number of extents in iloc box of a HEIC image.

### `heic:max-size-entity-group= value`

Sets the maximum size of an entity group of a HEIC image.

### `heic:max-children-per-box= value`

Sets the maximum number of children per box of a HEIC image.

### `heic:preserve-cicp= false`

Do not preserve the source HEIC CICP color information when writing HEIC output.

### `heic:preserve-clli= false`

Do not preserve the source HEIC content light level information when writing HEIC output.

### `heic:preserve-orientation= true`

Preserve the original EXIF orientation during HEIC decoding and rotate the pixels accordingly. By default, EXIF orientation is reset to "1" to match the actual orientation of pixels in HEIC.

### `heic:speed= value`

Set the HEIC speed parameter. Integer value from 0-9. Default is 5.

## histogram

### `histogram:unique-colors= false`

Suppress the textual listing of the image's unique colors.

## hough-lines

### `hough-lines:accumulator=true`

Return the accumulator image in addition to the lines image.

## icon

### `icon:auto-resize`

Automatically stores multiple sizes when writing an ico image (requires a 256x256 input image).

### `icon:png-compression-size`

Set the minimum image size threshold above which a PNG image is stored instead of a BMP image.

## identify

### `identify:convex-hull= true`

Display convex hull & minimum bounding box.

### `identify:locate= value`

Display minimum or maximum pixel locations. Valid values are minimum or maximum . The default is maximum .

### `identify:limit= value`

The maximum number of pixel locations to display when using identify:locate .

## image

### `image:frames`

Select specific frames from multi‑image formats, e.g., -define image:frames=0-3 .

## jp2

### `jp2:layer-number= value`

Set the maximum number of quality layers to decode. Same for JPT, JC2, and J2K.

### `jp2:number-resolutions= value`

Set the number of resolutions to encode.Same for JPT, JC2, and J2K.

### `jp2:progression-order= value`

Choose from LRCP, RLCP, RPCL, PCRL or CPRL. Same for JPT, JC2, and J2K.

### `jp2:quality= value,value...`

Set the quality layer PSNR, given in dB. The order is from left to right in ascending order. The default is a single lossless quality layer. Same for JPT, JC2, and J2K.

### `jp2:rate= value`

Specify the compression factor to use while writing JPEG-2000 files. The compression factor is the reciprocal of the compression ratio. The valid range is 0.0 to 1.0, with 1.0 indicating lossless compression. If defined, this value overrides the -quality setting. A quality setting of 75 results in a rate value of 0.06641. Same for JPT, JC2, and J2K.

### `jp2:reduce-factor= value`

Set the number of highest resolution levels to be discarded.Same for JPT, JC2, and J2K.

## jpeg

### `jpeg:arithmetic-coding= on|off`

enable/disable Huffman optimization.

### `jpeg:block-smoothing= on|off`



### `jpeg:colors= value`

Set the desired number of colors and let the JPEG encoder do the quantizing.

### `jpeg:dct-method= value`

Choose from default , fastest , float , ifast , and islow .

### `jpeg:extent= value`

Restrict the maximum JPEG file size, for example -define jpeg:extent=400KB . The JPEG encoder will search for the highest compression quality level that results in an output file that does not exceed the value. The -quality option also will be respected starting with version 6.9.2-5. Between 6.9.1-0 and 6.9.2-4, add -quality 100 in order for the jpeg:extent to work properly. Prior to 6.9.1-0, the -quality setting was ignored.

### `jpeg:fancy-upsampling= on|off`



### `jpeg:high-bit-depth= on|off`

By default, ImageMagick generates JPEG images at 8‑bit depth. When high bit‑depth is enabled, it will produce 12‑bit or 16‑bit images if the source image depth exceeds 8 bits.

### `jpeg:optimize-coding= on|off`



### `jpeg:q-table= table`



### `jpeg:restart-interval= value`

Set the restart interval to `interval` MCU blocks.

### `jpeg:sampling-factor= sampling-factor-string`



### `jpeg:size= geometry`

Set the size hint of a JPEG image, for example, -define jpeg:size=128x128 . It is most useful for increasing performance and reducing the memory requirements when reducing the size of a large JPEG image.

## json

### `json:features`

Include features in verbose information.

### `json:limit`



### `json:locate`



### `json:moments`

Include image moments in verbose information.

## jxl

### `jxl:decoding-speed= value`

Set the JPEG XL decoding speed. Valid values are in the range of 0 (slowest) to 4 (fastest, at the cost of some quality/density).

### `jxl:distance= value`

Set the JPEG XL encoder’s frame distance.

### `jxl:effort= value`

Set the JPEG XL encoding effort. Valid values are in the range of 3 (falcon) to 9 (tortoise).

### `jxl:quality= value`

Set the JPEG XL encoder’s frame distance.

## kmeans

### `kmeans:seed-colors= color-list`

Initialize the colors, where color-list is a semicolon delimited list of seed colors (e.g. red;sRGB(19,167,254);#00ffff)

## magick

### `magick:format= value`

Set the image encoding format use when writing a C-style header. This is the same as "h:format=format" described above.

## magnify

### `magnify:method= value`

Choose the method of pixel art magnification. The choices are: eagle2X, eagle3X, eagle3XB, epb2X, fish2X, hq2X, scale2X (default), scale3X, xbr2X

## minimum-bounding-box

### `minimum-bounding-box:orientation= value`

Find smallest perpendicular distance from edge to origin. Valid values are horizontal and vertical .

## mng

### `mng:need-cacheoff`

turn playback caching off for streaming MNG.

## modulate

### `modulate:colorspace= colorspace`

Define the colorspace to use with -modulate . Any hue-based colorspace may be use. The default is HSL.

## morphology

### `morphology:compose= compose-method`

Specify how to merge results generated by multiple -morphology kernel. The default is none. One typical value is 'lighten' as used, for example, with the sobel edge kernels.

### `morphology:showKernel= 1`

Output (to 'standard error') all the information about a generated -morphology kernel.

## pango

### `pango:align= left|center|right`



### `pango:auto-dir= true|false`



### `pango:ellipsize= start|middle|end`



### `pango:gravity-hint= natural|strong|line`



### `pango:hinting= none|auto|full`



### `pango:indent= points`



### `pango:justify= true|false`



### `pango:language= en_US|others`



### `pango:markup= true|false`



### `pango:single-paragraph= true|false`



### `pango:wrap= word|char|word-char`



## pcl

### `pcl:fit-to-page= true`



## pdf

### `pdf:author= author`

Sets the author of the document

### `pdf:create-epoch= seconds`

Sets the creation time of the document

### `pdf:creator= creator`

Sets the creator of the document

### `pdf:fit-page= geometry`

Geometry specifies the scaling dimensions for resizing when the PDF is being read. The geometry is either WxH&#123%} or page size. No offsets are allowed. (introduced in IM 6.8.8-8)

### `pdf:fit-to-page= true`



### `pdf:hide-annotations= true`

hide annotations associated with the page Annots key.

### `pdf:interpolate= true`

enable interpolation while rendering

### `pdf:keywords= keywords`

Sets the keywords of the document

### `pdf:modify-epoch= seconds`

Sets the modification time of the document

### `pdf:no-identifier= true`

Do not generate the ID entry

### `pdf:page-direction= right-to-left`



### `pdf:printed= true`

Determines whether the file should be displayed or printed using the "screen" or "printer" options for annotations and images.

### `pdf:producer= producer`

Sets the producer of the document

### `pdf:subject= subject`

Sets the subject of the document

### `pdf:stop-on-error= true`



### `pdf:thumbnail= false`

Generate image thumbnails when saving a PDF file.

### `pdf:title= title`

Sets the title of the document

### `pdf:use-cropbox= true`



### `pdf:use-trimbox= true`



## phash

### `phash:colorspaces= colorspace,colorspace,...`

The perceptual hash defaults to the xyY and HSB colorspaces. When using this define, you can specify up to six alternative colorspaces. (as of IM 7.0.3-8)

### `phash:normalize= true`

Normalize the phash metric

## pixel

### `pixel:compliance= {none|undefined|svg|mvg|x11|xpm}`

In combination with -depth , this define allows color values to be presented in one or combination of: percent, names, 8-bit components, or hex values. 16-bit depth values are generally shown as percents and 8-bit depth values generally are shown as a combination of color names and 8-bit component values.

### `pixel:compliance= value`

Set the "pixel:" output format according to several standards. The choices are SVG, None, Undefined, MVG, X11, XPM. The default list values for (s)RGB colors in the form of (s)rgb(r,g,b) or (s)rgba(r,g,b,a). Color names will no longer be presented. For sRGB or RGB colors, the SVG, X11, XPM and None options lists color names, if they exist. The MVG and Undefined options list hex values. When colors are presented or converted to hue-based colorspaces, the values listed will be integers for hue and percents for the other two components. For other colorspaces, values may be listed as either percents or fractional value. Setting the depth to 8 will limit values to the 8-bit range, except for hue-based colors.

## png

### `png:bit-depth= value`



### `png:chunk-malloc-max= value`

Set the maximum chunk size.

### `png:color-type= value`

Desired bit-depth and color-type for PNG output. You can force the PNG encoder to use a different bit-depth and color-type than it would have normally selected, but only if this does not cause any loss of image quality. Any attempt to reduce image quality is treated as an error and no PNG file is written. E.g., if you have a 1-bit black-and-white image, you can use these "defines" to cause it to be written as an 8-bit grayscale, indexed, or even a 64-bit RGBA. But if you have a 16-million color image, you cannot force it to be written as a grayscale or indexed PNG. If you wish to do this, you must use the appropriate -depth , -colors , or -type directives to reduce the image quality prior to using the PNG encoder. Note that in indexed PNG files, "bit-depth" refers to the number of bits per index, which can be 1, 2, 4, or 8. In such files, the color samples always have 8-bit depth.

### `png:compression-filter= value`

Valid values are 0 through 9. 0-4 are the corresponding PNG filters, 5 means adaptive filtering except for images with a colormap, 6 means adaptive filtering for all images, 7 means MNG "loco" compression, 8 means Z_RLE strategy with adaptive filtering, and 9 means Z_RLE strategy with no filtering.

### `png:compression-level= value`

Valid values are 0 through 9, with 0 providing the least, but fastest compression and 9 usually providing the best and always the slowest.

### `png:compression-strategy= value`

Valid values are 0 through 4, meaning default, filtered, huffman_only, rle, and fixed ZLIB compression strategy. If you are using an old zlib that does not support Z_RLE (before 1.2.0) or Z_FIXED (before 1.2.2.2), values 3 and 4, respectively, will use the zlib default strategy instead.

### `png:format= value`

valid values are png8 , png24 , png32 , png48 , png64 , and png00 . This property is useful for specifying the specific PNG format to be used, when the usual method of prepending the format name to the output filename is inconvenient, such as when writing a PNG-encoded ICO file or when using mogrify . Value = png8 reduces the number of colors to 256, only one of which may be fully transparent, if necessary. The other values do not force any reduction of quality; it is an error to request a format that cannot represent the image data without loss (except that it is allowed to reduce the bit-depth from 16 to 8 for all formats). Value = png24 and png48 allow transparency, only if a single color is fully transparent and that color does not also appear in an opaque pixel; such transparency is written in a PNG tRNS chunk. Value = png00 causes the image to inherit its color-type and bit-depth from the input image, if the input was also a PNG.

### `png:exclude-chunk= value`



### `png:include-chunk= value`

ancillary chunks to be excluded from or included in PNG output. The value can be the name of a PNG chunk-type such as bKGD , a comma-separated list of chunk-names (which can include the word date , the word all , or the word none ). Although PNG chunk-names are case-dependent, you can use all lowercase names if you prefer. The "include-chunk" and "exclude-chunk" lists only affect the behavior of the PNG encoder and have no effect on the PNG decoder. As a special case, if the sRGB chunk is excluded and the gAMA chunk is included, the gAMA chunk will only be written if gamma is not 1/2.2, since most decoders do not assume sRGB for gAMA=0.45455 when no colorspace information is included in the PNG file. Because the list is processed from left to right, you can achieve this with a single define: -define png:include-chunk=none,gAMA As a special case, if the sRGB chunk is not excluded and the PNG encoder recognizes that the image contains the sRGB ICC profile, the PNG encoder will write the sRGB chunk instead of the entire ICC profile. To force the PNG encoder to write the sRGB profile as an iCCP chunk in the output PNG instead of the sRGB chunk, exclude the sRGB chunk. The critical PNG chunks IHDR , PLTE , IDAT , and IEND cannot be excluded. Any such entries appearing in the list will be ignored. If the ancillary PNG tRNS chunk is excluded and the image has transparency, the PNG colortype is forced to be 4 or 6 (GRAY_ALPHA or RGBA). If the image is not transparent, then the tRNS chunk isn't written anyhow, and there is no effect on the PNG colortype of the output image. The -strip option does the equivalent of the following for PNG output: -define png:exclude-chunk=EXIF,iCCP,iTXt,sRGB,tEXt,zCCP,zTXt,date The default behavior is to include all known PNG ancillary chunks plus ImageMagick's private vpAg ("virtual page") chunk, and to exclude all PNG chunks that are unknown to ImageMagick, regardless of their PNG "copy-safe" status as described in the PNG specification. Any chunk names that are not known to ImageMagick are ignored if they appear in either the "include-chunk" or "exclude-chunk" list. The ancillary chunks currently known to ImageMagick are bKGD , cHRM , gAMA , iCCP , oFFs , orNT , pHYs , sRGB , tEXt , tRNS , vpAg , and zTXt . You can also put date in the list to include or exclude the "Date:create" and "Date:modify" text chunks that ImageMagick normally inserts in the output PNG.

### `png:ignore-crc[= true ]`

When you know your image has no CRC or ADLER32 errors, this can speed up decoding. It is also helpful in debugging bug reports from "fuzzers".

### `png:preserve-colormap[= true ]`

Use the existing image->colormap. Normally the PNG encoder will try to optimize the palette, eliminating unused entries and putting the transparent colors first. If this flag is set, that behavior is suppressed.

### `png:preserve-iCCP[= true ]`

By default, the PNG decoder and encoder examine any ICC profile that is present, either from an iCCP chunk in the PNG input or supplied via an option, and if the profile is recognized to be the sRGB profile, converts it to the sRGB chunk. You can use -define png:preserve-iCCP to prevent this from happening; in such cases the iCCP chunk will be read or written and no sRGB chunk will be written. There are some ICC profiles that claim to be sRGB but have various errors that cause them to be rejected by libpng16; such profiles are recognized anyhow and converted to the sRGB chunk, but are rejected if the -define png:preserve-iCCP is present. Note that not all "sRGB" ICC profiles are recognized yet; we will add them to the list as we encounter them.

### `png:swap-bytes[= true ]`

The PNG specification requires that any multi-byte integers be stored in network byte order (MSB-LSB endian). This option allows you to fix any invalid PNG files that have 16-bit samples stored incorrectly in little-endian order (LSB-MSB). The "-define png:swap-bytes" option must appear before the input filename on the commandline. The swapping is done during the libpng decoding operation.

## precision

### `precision:highres-transform= true`

Increase the profile transform precision. Note, there is a slight performance penalty as the high-precision transform is floating point rather than unsigned. It is important to note that results may depend on whether or not the original image already has an included profile.

## profile

### `profile:skip= name1,name2,...`

Skip the named profile[s] when reading the image. Use skip="*" to skip all named profiles in the image. Many named profiles exist, including ICC, EXIF, APP1, IPTC, XMP, and others.

## ps

### `ps:imagemask`

If the ps:imagemask flag is defined, the PS3 and EPS3 coders will create Postscript files that render bilevel images with the Postscript imagemask operator instead of the image operator.

## psd

### `psd:additional-info=all|selective`

This option should only be used when converting from a PSD file to another PSD file. This should be placed after the image is read. The two options are 'all' and 'selective'. The 'selective' option will preserve all additional information that is not related to the geometry of the image. The 'all' option should only be used when the geometry of the image has not been changed. This option is helpful when transferring non-simple layers, such as adjustment layers from the input PSD file to the output PSD file. If this option is not used, the additional information will not be preserved. This define is available as of Imagemagick version 6.9.5-8.

### `psd:alpha-unblend=off`

Disable new automatic un-blending of transparency with the base image for the flattened layer 0 before adding the alpha channel to the output image. This define must be placed before the input psd image. (Available as of IM 6.9.2.5). The automatic un-blending is new to IM 6.9.2.5 and prevents the transparency from being applied twice in the output image. This option should be set before reading the image.

### `psd:preserve-opacity-mask= true`

This option should only be used when converting from a PSD file to another PSD file. It will preserve the opacity mask of a layer and add it back to the layer when the image is saved. Setting this to 'true' will enable this feature. This define is available as of Imagemagick version 6.9.5-10.

### `psd:write-layers= false`

This option can be used to disable writing the layers of a PSD file.

### `psd:replicate-profile= true`

This option can be used to copy the image profile to all the images instead of only the first image that is returned.

## ptif

### `ptif:pyramid= min-base x levels`

Specify the min-base and number of levels of the pyramid, e.g., 64x4.

## quantum

### `quantum:format= type`

Set the type to floating-point to specify a floating-point format for raw files (e.g. GRAY:) or for MIFF and TIFF images in HDRI mode to preserve negative values. If -depth 16 is included, the result is a single precision floating point format. If -depth 32 is included, the result is double precision floating point format. For signed pixel data, use -define quantum:format=signed

### `quantum:maximum= value`

Maximum value for certain image types such as DCM. If not set, the the maximum value is QuantumRange.

### `quantum:minimum= value`

Minimum value for certain image types such as DCM. If not set, the the minimum value is zero.

### `quantum:polarity= photometric-interpretation`

Set the photometric-interpretation of an image (typically for TIFF image file format) to either min-is-black (default) or min-is-white .

## registry

### `registry: attribute = value`

Set attributes of the image registry, for example, registry:temporary-path=/data/tmp.

### `registry:date:precision= length`

Set the maximum number of characters printed for any timestamp.

### `registry:option:pedantic= true | false`

By default, if a command-line option is also a filename (e.g., -quality), it is intrepetted as a filename. Set this option to true to interpret it as an option.

### `registry:precision= value`

Set the maximum number of significant digits to be printed.

## resample

### `resample:verbose= true`

Output the cylindrical filter lookup table created by the EWA (Elliptical Weighted Average) resampling algorithm. Note this table uses a squared radius lookup value. This is typically only used for debugging EWA resampling.

## sample

### `sample:offset= geometry`

Location of the sampling point within the sub-region being sampled, expressed as percentages (see -sample ).

## shepards

### `shepards:power= value`

Set the exponent in the Shepard's distortion. The default is 2.

## stream

### `stream:buffer-size= value`

Set the stream buffer size. Select 0 for unbuffered I/O.

## svg

### `svg:parse-huge= true`

Enable rendering of a very large SVG for which you trust the source.

### `svg:substitute-entities= true`

Enable entity substitution if you trust the source.

## tga

### `tga:preserve-orientation= true`

Preserve the image orientation.

### `tga:write-footer= true`

Enable writing of an empty optional footer.

## tiff

### `tiff:alpha= associated|unassociated|unspecified`

Specify the alpha extra samples as associated, unassociated or unspecified.

### `tiff:assume-alpha= true|false`

Assume undeclared extra channels are alpha.

### `tiff:endian= msb|lsb`



### `tiff:exif-properties= false`

Disable reading the EXIF properties.

### `tiff:fill-order= msb|lsb`



### `tiff:peg-tables-mode= 0-3`

Set the TIFFTAG_JPEGTABLESMODE when the tiff file is written with jpeg compression

### `tiff:gps-properties= false`

Disable reading the GPS properties.

### `tiff:ignore-layers= true`

Ignore the Photoshop layers.

### `tiff:ignore-tags= comma-separate-list-of-tag-IDs`

Allow one or more tag ID values to be ignored.

### `tiff:predictor= [1, 2 or 3]`

A mathematical operator that is applied to the image data before an encoding scheme is applied. The general idea is that subsequent pixels of an image resemble each other. Thus, substracting the information from a pixel that is already contained in previous one is likely to reduce its information density considerably and aid subsequent compression. 1 = No prediction scheme used before coding. 2 = Horizontal differencing. 3 = Floating point horizontal differencing.

### `tiff:preserve-compression= true`

Preserve compression of the source image.

### `tiff:rows-per-strip= value`

Set the number of rows per strip.

### `tiff:tile-geometry= WxH`

Set the tile size for pyramid tiffs. Requires the suffix PTIF: before the outputname.

## trim

### `trim:percent-background= X%`

Set the amount of background that is tolerated in an edge. It is specified as a percent. 0% means no background is tolerated. 50% means an edge can contain up to 50% pixels that are background per the fuzz-factor.

### `trim:edges={ north,east,south,west }`

Only trim the specified edges of the image.

### `trim:minSize= geometry`

Limit the trim to the specified size.

## txt

### `txt:compliance= value`

Set the "txt:" format for the values in parentheses according to several standards. The choices are svg, none, undefined, mvg, x11, xpm. The default will list values for (s)RGB colors in the quantum range. The SVG, X11, XPM, MVG and None options lists values in the 8-bit range for all Q-level compiles. The undefined option also lists values in the quantum range. When colors are presented or converted to hue-based colorspaces, the values listed will be integers for hue and percents for the other two components. For other colorspaces, values may be listed as either percents or fractional value. Setting the depth to 8 will limit values to the 8-bit range, except for hue-based colors.

## type

### `type:features= string`

Add a font feature to be used by the RAQM delegate during complex text layout. This is usually used to turn on optional font features that are not enabled by default, but can be also used to turn off default font features. Features include those to control kerning, ligature and Arabic.

### `type:hinting= false`

Disable font hinting. Proper glyph rendering needs the scaled points to be aligned along the target device pixel grid, through an operation often called hinting. One of its main purposes is to ensure that important widths and heights are respected throughout the whole font. (For example, it is very often desirable that the ‘I’ and the ‘T’ glyphs have their central vertical line of the same pixel width. Hinting also manages features like stems and overshoots, which can cause problems at small pixel sizes.

## uhdr

### `uhdr:gainmap-gamma= value`

Set gainmap image encoding gamma. Must be greater than 0.0. Used during encoding. Optional. Default value is 1.0.

### `uhdr:gainmap-quality= value`

Set gainmap image encoding quality factor. The valid range is 1 to 100, with 1 indicating lowest image quality or highest compression and 100 indicating best quality or least effective compression. Used during encoding. Optional. Default value is 95.

### `uhdr:gainmap-max-content-boost= value`

Specify the maximum allowed ratio of the linear luminance for the target HDR rendition relative to (divided by) that of the SDR image, at a given pixel. In other words, this specifies how much brighter a pixel can get, when shown on an HDR display, relative to the SDR rendition. Must be greater than 0.0. Used during encoding. Optional. If not configured, this is computed dynamically based on the input.

### `uhdr:gainmap-min-content-boost= value`

Specify the minimum allowed ratio of the linear luminance for the target HDR rendition relative to (divided by) that of the SDR image, at a given pixel. In other words, this specifies how much darker a pixel can get, when shown on an HDR display, relative to the SDR rendition. Must be greater than 0.0. Used during encoding. Optional. If not configured, this is computed dynamically based on the input.

### `uhdr:hdr-color-gamut= {bt709|display_p3|bt2100}`

Set input HDR intent color gamut. Used during encoding. Required.

### `uhdr:hdr-color-transfer= {hlg|pq|linear}`

Set input HDR intent color transfer. Used during encoding. Required.

### `uhdr:output-color-transfer= {hlg|pq|linear|srgb}`

Set the target display transfer characteristics on which the ultrahdr image is rendered. Used during decoding. Required. If srgb , only sdr intent is decoded and sent as output, otherwise, sdr intent and gainmap are decoded, combined into hdr image and sent as output.

### `uhdr:sdr-color-gamut= {bt709|display_p3|bt2100}`

Set input SDR intent color gamut. Used during encoding. Required.

### `uhdr:uhdr:target-display-peak-brightness= value`

Peak brightness refers to the maximum brightness level that a display can achieve. This is important for accurately representing bright highlights in HDR content.

## video

### `video:intermediate-format= {pam,webp}`

Set the video intermediate format option of ffmpeg .

### `video:pixel-format= value`

Set the pixel format option of ffmpeg .

### `video:vsync= value`

Set the vsync option of ffmpeg .

## webp

### `webp: tag = value`

WebP has a plethora of defines detailed on this page .

## white-balance

### `white-balance:vibrance= value&#123%}`

Change in color vibrance of the a & b channels.

## x

### `x:screen= true`

Obtain the image from the root window.

### `x:silent= true`

Turn off the beep when importing an image.

## xmp

### `xmp:validate= {true,false}`

By default, ImageMagick validates any XMP profile embedded in an image.
