// cppimport
#include <pybind11/pybind11.h>

namespace py = pybind11;

// The computational routine
void processFrame(unsigned short *inFrame, int samplesPerPixel, int linesPerFrame,
        int pixelsPerLine, int flipEvenRows, unsigned short *outFrame)
{
    // declare variables
    int i;
    int j;
    int k;
    double sampleValue;
    double pixelSum;
    int pixelCount;
    int index;
    bool doFlip = flipEvenRows;  // initialise doFlip to flip either even or odd rows
    
    // ROW LOOP
    for (i=0; i<linesPerFrame; i++) {
        
        // toggle whether or not to flip this line
        doFlip = !doFlip;
        
        // COLUMN LOOP
        for (j=0; j<pixelsPerLine; j++) {
            
            // SAMPLE LOOP
            sampleValue = 0;
            pixelSum = 0;
            pixelCount = 0;
            for (k=0; k<samplesPerPixel; k++) {
                sampleValue = inFrame[(i*linesPerFrame*samplesPerPixel) + (j*samplesPerPixel) + k];
                sampleValue -= 8192;
                if (sampleValue >= 0) {
                    pixelSum += sampleValue;
                    pixelCount += 1;
                }
            }
            
            if (doFlip) {
                index = (i*linesPerFrame) + (pixelsPerLine - 1 - j);
            }
            else {
                index = (i*linesPerFrame) + j;
            }
            outFrame[index] = pixelSum / pixelCount;
        }
    }
}


PYBIND11_MODULE(PrairieLink_ProcessFrame, m) {
    m.def("processFrame", &processFrame, "A function that seems to process Prarie datastream",
    py::arg("inFrame"), py::arg("samplesPerPixel"), py::arg("linesPerFrame"), py::arg("pixelsPerLine"), py::arg("flipEvenRows"));
    m.attr("outFrame") = outFrame;
}

PYBIND11_MODULE(somecode, m) {
    m.def("square", &square);
}
/*
<%
setup_pybind11(cfg)
%>
*/