#include <stdio.h>
#include <iostream>
#include <opencv2/opencv.hpp>

using namespace std;
using namespace cv;

Mat primary_src_image = imread("ximea.png",CV_LOAD_IMAGE_GRAYSCALE);


Mat morphImage(Mat src_image, int rows, int cols){
	Mat morphed_image;
	Mat morph_kernel = getStructuringElement(MORPH_RECT, Size(cols,rows));
	erode(src_image, morphed_image, morph_kernel, Point(-1,-1));
	//dilate(src_image, morphed_image, morphKernel, Point(-1,-1));
	return morphed_image;
}


Mat detectEdges(Mat src_image, double threshold1, double threshold2,
				int kernel_size = 3){
	Mat edgy_image;
	Canny(src_image,edgy_image,threshold1,threshold2,kernel_size);
	return edgy_image;
}


Mat convert2binary(Mat src_image, double binary_threshold,
					bool use_adaptive = false, int kernel_size = 3){

	Mat binary_image;
	if(use_adaptive == false){ 
		threshold(src_image,binary_image,binary_threshold,255,CV_THRESH_BINARY);
		return binary_image;
	}
	else{
		adaptiveThreshold(src_image,binary_image, 255.0, CV_ADAPTIVE_THRESH_MEAN_C, CV_THRESH_BINARY, kernel_size, 0);
	}
	return binary_image;
}


Mat convert2Grayscale(Mat src_image){
	Mat gray_image;
	if(src_image.channels() == 3){
		cvtColor(src_image,gray_image,CV_BGR2GRAY);
	}
	else {
		gray_image = src_image;
	}

	return gray_image;
}

void displayImage(Mat image, String image_name){
	imshow(image_name,image);
}


void saveImage(Mat image, String image_name){
	imwrite(image_name,image);
}


void displayAndSave(Mat image, String image_name){
        cout << "displaying and saving "+image_name << std::endl;
	displayImage(image,image_name);
	saveImage(image,image_name);
}


Mat retrieveVerticalEdges(const Mat src_image, int threshold1 = 255, int threshold2=225, int vertical_size = 5){
	Mat working_image;
	displayAndSave(src_image, "original.png");
	
	//converting to grayscale if not already
	working_image = convert2Grayscale(src_image);
	displayAndSave(working_image,"grayscale.png");	
        cout << "converted to grayscale" << std::endl;


/*	working_image = convert_to_binary(working_image,binaryThreshold, true);
	displayAndSave(working_image,"binary.png");
        cout << "converted to binary" << std::endl;
*/

	//Generating edge map
	working_image = detectEdges(src_image,threshold1,threshold2);
	displayAndSave(working_image,"edge_detected.png");
        cout << "detected edges" << std::endl;
	
	// //pulling out horizontal edges
	// int horizontal_size = 5; //working_image.cols / 150; //Hardcoded 30 here, but a smaller kernel dimension may be fine
	// Mat horizontal_image = morph_image(working_image, 1, horizontal_size);
	// displayAndSave(horizontal_image,"horizontal_edges.png");        
 //        cout << "horizontal morphed" << std::endl;
	
	//pulling out vertical edges 
	Mat vertical_image = morphImage(working_image, vertical_size, 1);
	displayAndSave(vertical_image, "vertical_edges.png");
    cout << "vertical morphed" << std::endl;

    return vertical_image;
}


int findPoint(Vec4f line, int y){
	int x1 = line[0];
	int y1 = line[1];
	int x2 = line[2];
	int y2 = line[3];
	return (y-y1) * ((x2-x1) / (y2-y1)) + x1;
}

Mat calculateRawDistances(Mat src_image, int max_line_break = 50){
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

	Mat distances(src_image.rows,1,CV_8UC1); //matrix for distances between pixels N x 1 dimensions
	Mat line_image(src_image.rows,src_image.cols,CV_8UC3); //matrix specifically for lines, same shape as src
	vector<Vec4i> lines; 
	cout << "about to perform Hough transform" << std::endl;
	HoughLinesP(src_image, lines, 1, CV_PI/180, 25, 100, max_line_break);
	cout << "Hough performed" << std::endl;
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
		cout << "more than 2 lines. computation is impossible" << std::endl;
		distances.setTo(-1);
	}
	else{
		for(int row = 0; row < distances.rows; row++){
			int pixelDistance = findPoint(lines[1],row) - findPoint(lines[0],row);
			distances.at<uchar>(row,1) = pixelDistance;
		}
	}
	return distances;
}


int main(int argc, char const *argv[])
{
	/* code */
	
	if(! primary_src_image.data){
            cout << "unable to read image" << std::endl;
            return -1;
        }

        Mat vertical_image = retrieveVerticalEdges(primary_src_image,225,255,5);
        Mat raw_distances = calculateRawDistances(vertical_image);
        cout << "raw_distances = " << std::endl << raw_distances << endl << "end of distance matrix"; 

        cout << "Swag young thug\n"; 
        waitKey(0);
	return 0;
}

