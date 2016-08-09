#include "includes.hpp"

#if !defined(KERNAL_SIZE)
#define KERNAL_SIZE 3
#endif

Mat primary_src_image = imread("ximea.png",CV_LOAD_IMAGE_GRAYSCALE);

void displayAndSave(Mat image, String image_name){
    cout << "displaying and saving "+image_name << std::endl;
    cv::imshow(image_name,image);
    cv::imwrite(image_name,image);
}

/**
* Takes a matrix and detects the 2 lines in the ibeam gap
*/
Mat retrieveVerticalEdges(const Mat src_image, int threshold1 = 255, int threshold2=225, int vertical_size = 5) {
    register Mat working_image = src_image;
#if defined DEBUG
    displayAndSave(src_image, "original.png");
#endif
    //converting to grayscale if not already
    if (working_image.channels() == 3) {
        cvtColor(src_image, working_image, CV_BGR2GRAY);
    }
#if defined DEBUG
    displayAndSave(working_image, "grayscale.png");	
    cout << "converted to grayscale" << std::endl;
#endif

    //Generating edge map
    Canny(working_image, working_image, threshold1, threshold2, KERNAL_SIZE);
#if defined DEBUG    
    displayAndSave(working_image,"edge_detected.png");
    cout << "detected edges" << std::endl;
#endif

    //pulling out vertical edges 
    Mat morph_kernel = getStructuringElement(MORPH_RECT, Size(vertical_size, 1));
    erode(working_image, working_image, morph_kernel, Point(-1,-1));

#if defined DEBUG
    displayAndSave(working_image, "vertical_edges.png");
    cout << "vertical morphed" << std::endl;
#endif

    return working_image;
}

/**
* Calculates Integer point location from vector given an offset of y
*/
int findPoint(Vec4f line, int y){
        //using definitions direct from line for optimization
	//x1 = line[0], y1 = line[1], x2 = line[2], y2 = line[3];
	return (y - line[1]) * ((line[2] - line[0]) / (line[3] - line[1])) + line[0];
}

/*
    Eventually two types should be implemented!
    Type 0 
        utilizes the probablistic Hough Line transform to generate the equations of two lines
        distance between the two line is calculated by subracting the two
        and multiplying by the pixel_displacement_ratio
    Type 1
        uses multiple for loops to go through the image row by row
        and subtract distances left to right
*/
Mat calculateRawDistances(const Mat src_image, int max_line_break = 50) {
    Mat distances(src_image.rows,1,CV_8UC1); //matrix for distances between pixels N x 1 dimensions
    Mat line_image(src_image.rows,src_image.cols,CV_8UC3); //matrix specifically for lines, same shape as src
    vector<Vec4i> lines;
#if defined DEBUG 
    cout << "About to perform Hough transform" << std::endl;
#endif
    HoughLinesP(src_image, lines, 1, CV_PI/180, 25, 100, max_line_break);
#if defined DEBUG
    cout << "Hough performed" << std::endl;
#endif
    //putting lines on an image for display and verifications purposes
    for( size_t i = 0; i < lines.size(); i++ ){
        Vec4i single_line = lines[i];
        line(line_image, Point(single_line[0], single_line[1]), Point(single_line[2], single_line[3]), Scalar(0,0,255), 3, CV_AA);
    }
    Mat line_overlay_image;
    cvtColor(src_image,line_overlay_image,CV_GRAY2RGB);
    displayAndSave(line_overlay_image+line_image,"image_with_lines.png");

    //Calculating distances
    if(lines.size() > 2){ //rejecting if there are more than two lines in this image
#if defined DEBUG
        //Instead of just closign, should we grab the two largest vertical lines?
        cout << "more than 2 lines. computation is impossible" << std::endl;
#endif
        distances.setTo(-1);
    }
    else {
        for(int row = 0; row < distances.rows; row++){
                int pixelDistance = findPoint(lines[1],row) - findPoint(lines[0],row);
                distances.at<uchar>(row,1) = pixelDistance;
        }
    }
    return distances;
}

/*
int main(int argc, char const *argv[])
{
    if(! primary_src_image.data){
        cout << "Unable to read image" << std::endl;
        return EXIT_FAILURE;;
    }

    Mat vertical_image = retrieveVerticalEdges(primary_src_image,225,255,5);
    Mat raw_distances = calculateRawDistances(vertical_image);
    cout << "raw_distances = " << std::endl << raw_distances << endl << "end of distance matrix"; 
    
    return EXIT_SUCCESS;;
}
*/
