//# Copyright (C) 1998,1999,2000,2001,2003
//# Associated Universities, Inc. Washington DC, USA.
//#
//# This program is free software; you can redistribute it and/or modify it
//# under the terms of the GNU General Public License as published by the Free
//# Software Foundation; either version 2 of the License, or (at your option)
//# any later version.
//#
//# This program is distributed in the hope that it will be useful, but WITHOUT
//# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
//# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
//# more details.
//#
//# You should have received a copy of the GNU General Public License along
//# with this program; if not, write to the Free Software Foundation, Inc.,
//# 675 Massachusetts Ave, Cambridge, MA 02139, USA.
//#
//# Correspondence concerning AIPS++ should be addressed as follows:
//#        Internet email: aips2-request@nrao.edu.
//#        Postal address: AIPS++ Project Office
//#                        National Radio Astronomy Observatory
//#                        520 Edgemont Road
//#                        Charlottesville, VA 22903-2475 USA
//#
//# $Id: $

#include <imageanalysis/ImageAnalysis/ImageTask.h>
#include <coordinates/Coordinates/DirectionCoordinate.h>
#include <casa/IO/FilebufIO.h>
#include <casa/OS/Directory.h>
#include <casa/OS/RegularFile.h>
#include <casa/OS/SymLink.h>
#include <images/Images/FITSImage.h>
#include <images/Images/ImageUtilities.h>
#include <images/Images/MIRIADImage.h>
#include <images/Images/PagedImage.h>
#include <images/Images/TempImage.h>

#include <imageanalysis/ImageAnalysis/ImageHistory.h>
#include <imageanalysis/ImageAnalysis/ImageInputProcessor.h>
#include <imageanalysis/ImageAnalysis/ImageMask.h>
#include <imageanalysis/ImageAnalysis/SubImageFactory.h>
#include <imageanalysis/IO/LogFile.h>
#include <stdcasa/variant.h>

namespace casa {

template <class T> ImageTask<T>::ImageTask(
	const SPCIIT image,
	const String& region, const Record *const &regionPtr,
	const String& box, const String& chanInp,
	const String& stokes, const String& maskInp,
    const String& outname, Bool overwrite
) : _image(image), _regionPtr(regionPtr),_region(region), _box(box),
	_chan(chanInp), _stokesString(stokes), _mask(maskInp),
	_outname(outname), _overwrite(overwrite), _stretch(False),
	_logfile() {
   // FITSImage::registerOpenFunction();
   //  MIRIADImage::registerOpenFunction();
}

template <class T> ImageTask<T>::ImageTask(
	const SPCIIT image, const Record *const &regionPtr,
	const String& mask,
    const String& outname, Bool overwrite
) : _image(image), _regionPtr(regionPtr),
	_region(), _box(), _chan(), _stokesString(), _mask(mask),
	_outname(outname), _overwrite(overwrite) {
	//FITSImage::registerOpenFunction();
	//MIRIADImage::registerOpenFunction();
}

template <class T> ImageTask<T>::~ImageTask() {}

template <class T> std::vector<OutputDestinationChecker::OutputStruct> ImageTask<T>::_getOutputStruct() {
	std::vector<OutputDestinationChecker::OutputStruct> outputs;
    _outname.trim();
    if (! _outname.empty()) {
        OutputDestinationChecker::OutputStruct outputImage;
        outputImage.label = "output image";
        outputImage.outputFile = &_outname;
        outputImage.required = True;
        outputImage.replaceable = _overwrite;
        outputs.push_back(outputImage);
    }
    return outputs;
}

template <class T> void ImageTask<T>::_construct(Bool verbose) {
	ThrowIf(
		! _supportsMultipleBeams() && _image->imageInfo().hasMultipleBeams(),
		"This application does not support images with multiple "
		"beams. Please convolve your image with a single beam "
		"and run this application using that image"
	);
	String diagnostics;
	std::vector<OutputDestinationChecker::OutputStruct> outputs = _getOutputStruct();
	std::vector<OutputDestinationChecker::OutputStruct> *outputPtr = outputs.size() > 0
		? &outputs
		: 0;
	std::vector<Coordinate::Type> necCoords = _getNecessaryCoordinates();
	std::vector<Coordinate::Type> *coordsPtr = necCoords.size() > 0
		? &necCoords
		: 0;
	ThrowIf(
		_mustHaveSquareDirectionPixels()
		&& _image->coordinates().hasDirectionCoordinate()
		&& ! _image->coordinates().directionCoordinate().hasSquarePixels(),
		"This application requires that the input image must have square"
		"direction pixels, but the input image does not. Please regrid it"
		"so it does and rerun on the regridded image"
	);
	ImageInputProcessor inputProcessor;
	inputProcessor.process(
		_regionRecord, diagnostics, outputPtr,
    	_stokesString, _image, _regionPtr,
    	_region, _box, _chan,
    	_getStokesControl(), _supportsMultipleRegions(),
    	coordsPtr, verbose
    );
}

template <class T> void ImageTask<T>::setRegion(const Record& region) {
	ThrowIf(
		! _supportsMultipleRegions() && region.isDefined("regions"),
		"This application does not support multiple region selection"
	);
    _regionRecord = region;
    _box = "";
    _chan = "";
    _stokesString = "";
    _region = "";
}

template <class T> void ImageTask<T>::_removeExistingFileIfNecessary(
	const String& filename, Bool overwrite
) {
	File out(filename);
	if (out.exists()) {
		// remove file if it exists which prevents emission of
		// file is already open in table cache exceptions
		if (overwrite) {
			if (out.isDirectory()) {
				Directory dir(filename);
				dir.removeRecursive();
			}
			else if (out.isRegular()) {
				RegularFile reg(filename);
				reg.remove();
			}
			else if (out.isSymLink()) {
				SymLink link(filename);
				link.remove();
			}
		}
		else {
			ThrowCc(
				"File " + filename + " exists but overwrite is false "
				"so it cannot be overwritten"
			);
		}
	}
}

template <class T> void ImageTask<T>::_removeExistingOutfileIfNecessary() const {
	_removeExistingFileIfNecessary(_outname, _overwrite);
}

template <class T> String ImageTask<T>::_summaryHeader() const {
	String region = _box.empty() ? _region : "";
	ostringstream os;
	os << "Input parameters ---" << endl;
	os << "       --- imagename:           " << _image->name() << endl;
	os << "       --- region:              " << region << endl;
	os << "       --- box:                 " << _box << endl;
	os << "       --- channels:            " << _chan << endl;
	os << "       --- stokes:              " << _stokesString << endl;
	os << "       --- mask:                " << _mask << endl;
	return os.str();
}

template <class T> void ImageTask<T>::setLogfile(const String& lf) {
	if (lf.empty()) {
		return;
	}
	ThrowIf(
		! _hasLogfileSupport(),
		"Logic Error: This task does not support writing of a log file"
	);
	try {
		_logfile.reset(new LogFile(lf));
		_logfile->setAppend(_logfileAppend);
	}
	catch (const AipsError& x) {}
}

template <class T> const SHARED_PTR<LogFile> ImageTask<T>::_getLogFile() const {
	ThrowIf(
		! _hasLogfileSupport(),
		"Logic Error: This task does not support writing of a log file"
	);
	return _logfile;
}

template <class T> Bool ImageTask<T>::_openLogfile() {
	if (_logfile.get() == 0) {
		return False;
	}
	ThrowIf(
		! _hasLogfileSupport(),
		"Logic Error: This task does not support writing of a log file"
	);
	return _logfile->open();
}

template <class T> void ImageTask<T>::_closeLogfile() const {
	if (_logfile) {
		_logfile->close();
	}
}

template<class T> Bool ImageTask<T>::_writeLogfile(
	const String& output, const Bool open, const Bool close
) {
	ThrowIf(
		! _hasLogfileSupport(),
		"Logic Error: This task does not support writing of a log file"
	);
	if (! _logfile) {
		return False;
	}
	return _logfile->write(output, open, close);
}

template <class T> void ImageTask<T>::setLogfileAppend(Bool a) {
	ThrowIf(
		! _hasLogfileSupport(),
		"Logic Error: This task does not support writing of a log file"
	);
	_logfileAppend = a;
	if (_logfile) {
		_logfile->setAppend(a);
	}
}

template <class T> void ImageTask<T>::addHistory(
	const vector<std::pair<String, String> >& msgs
) const {
	_newHistory.insert(
		_newHistory.end(), msgs.begin(), msgs.end()
	);
}

template <class T> void ImageTask<T>::addHistory(
	const LogOrigin& origin, const String& msg
) const {
	std::pair<String, String> x;
	x.first = origin.fullName();
	x.second = msg;
	_newHistory.push_back(x);
}

template <class T> void ImageTask<T>::addHistory(
	const LogOrigin& origin, const vector<String>& msgs
) const {
	std::pair<String, String> x;
	x.first = origin.fullName();
	for( String m: msgs ) {
		x.second = m;
		_newHistory.push_back(x);
	}
}

template <class T> void ImageTask<T>::addHistory(
    const LogOrigin& origin, const String& taskname,
    const vector<String>& paramNames, const vector<casac::variant>& paramValues
) const {
	ThrowIf(
		paramNames.size() != paramValues.size(),
		"paramNames and paramValues must have the same number of elements"
	);
	std::pair<String, String> x;
	x.first = origin.fullName();
	x.second = "Ran " + taskname + " on " + _image->name();
	_newHistory.push_back(x);
	vector<std::pair<String, casac::variant> > inputs;
	vector<String>::const_iterator begin = paramNames.begin();
	vector<String>::const_iterator name = begin;
	vector<casac::variant>::const_iterator value = paramValues.begin();
	vector<String>::const_iterator end = paramNames.end();
	String out = taskname + "(";
	String quote;
	while (name != end) {
		if (name != begin) {
			out += ", ";
		}
		quote = value->type() == casac::variant::STRING ? "'" : "";
		out += *name + "=" + quote;
		out += value->toString();
		out += quote;
		name++;
		value++;
	}
	x.second = out + ")";
	_newHistory.push_back(x);
}

template <class T> void ImageTask<T>::_copyMask(
	Lattice<Bool>& mask, const ImageInterface<T>& image
) {
	auto cursorShape = image.niceCursorShape(4096*4096);
	LatticeStepper stepper(image.shape(), cursorShape, LatticeStepper::RESIZE);
	RO_MaskedLatticeIterator<T> iter(image, stepper);
	LatticeIterator<Bool> miter(mask, stepper);
	std::unique_ptr<RO_LatticeIterator<Bool>> pmiter;
	if (image.hasPixelMask()) {
		pmiter.reset(new RO_LatticeIterator<Bool>(image.pixelMask(), stepper));
	}
	for (iter.reset(); ! iter.atEnd(); ++iter, ++miter) {
		auto mymask = iter.getMask();
		if (pmiter) {
			mymask = mymask && pmiter->cursor();
			pmiter->operator++();
		}
		miter.rwCursor() = mymask;
	}
}

template <class T> void ImageTask<T>::_copyData(
	Lattice<T>& data, const ImageInterface<T>& image
) {
	auto cursorShape = image.niceCursorShape(4096*4096);
	LatticeStepper stepper(image.shape(), cursorShape, LatticeStepper::RESIZE);
	RO_LatticeIterator<T> iter(image, stepper);
	LatticeIterator<T> diter(data, stepper);
	for (iter.reset(); ! iter.atEnd(); ++iter, ++diter) {
		diter.rwCursor() = iter.cursor();
	}
}

template <class T> SPIIT ImageTask<T>::_prepareOutputImage(
    const ImageInterface<T>& image, const Array<T> *const values,
    const ArrayLattice<Bool> *const mask,
    const IPosition *const outShape, const CoordinateSystem *const coordsys,
	const String *const outname, Bool overwrite, Bool dropDegen
) const {
    /*
	_timer.stop();
	cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
	_timer.start();
	*/
	IPosition oShape = outShape == 0 ? image.shape() : *outShape;
	CoordinateSystem csys = coordsys == 0 ? image.coordinates() : *coordsys;
	/*
	_timer.stop();
	cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
	_timer.start();
	*/
	SHARED_PTR<TempImage<T> > tmpImage(
		new TempImage<T>(TiledShape(oShape), csys)
	);
	/*
	_timer.stop();
	cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
	_timer.start();
	*/
	if (mask != 0) {
		if (! ImageMask::isAllMaskTrue(*mask)) {
			tmpImage->attachMask(*mask);
		}
	}
	// because subimages can have two types of masks, a region mask and
	// a pixel mask, but most other types of images really just have a
	// pixel mask. its very confusing
	else if (image.hasPixelMask() || image.isMasked()) {
		// A paged array is stored on disk and is preferred over an
		// ArrayLattice which will exhaust memory for large images.
	    /*
		_timer.stop();
		cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
		_timer.start();
		*/
		std::unique_ptr<Lattice<Bool>> mymask;
		if (image.size() > 4096*4096) {
			mymask.reset(new PagedArray<Bool>(image.shape()));
		}
		else {
			mymask.reset(new ArrayLattice<Bool>(image.shape()));
		}
		/*
		_timer.stop();
		cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
		_timer.start();
		*/
		_copyMask(*mymask, image);
		/*
		_timer.stop();
		cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
		_timer.start();
		*/
		if (! ImageMask::isAllMaskTrue(image)) {
		    /*
			_timer.stop();
			cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
			_timer.start();
			*/
			tmpImage->attachMask(*mymask);
		}
		/*
		_timer.stop();
		cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
		_timer.start();
		*/
	}
	String myOutname = outname ? *outname : _outname;
	if (! outname) {
		overwrite = _overwrite;
	}
	SPIIT outImage = tmpImage;
	if (values) {
		outImage->put(*values);
	}
	else {
	    /*
		_timer.stop();
		cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
		_timer.start();
		*/
		_copyData(*outImage, image);
		/*
		_timer.stop();
		cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
		_timer.start();
		*/
	}
	if (dropDegen || ! myOutname.empty()) {
		if (! myOutname.empty()) {
			_removeExistingFileIfNecessary(myOutname, overwrite);
		}
		/*
		_timer.stop();
		cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
		_timer.start();
		*/
		String emptyMask = "";
		Record empty;
        outImage = SubImageFactory<T>::createImage(
        	*tmpImage, myOutname, empty, emptyMask,
        	dropDegen, False, True, False
        );
        /*
    	_timer.stop();
    	cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
    	_timer.start();
    	*/
	}
	ImageUtilities::copyMiscellaneous(*outImage, image);
	/*
	_timer.stop();
	cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
	_timer.start();
	*/
	if (! _suppressHistory) {
		ImageHistory<T> history(outImage);
		vector<std::pair<String, String> >::const_iterator end = _newHistory.end();
		vector<std::pair<String, String> >::const_iterator iter = _newHistory.begin();
		while (iter != end) {
			history.addHistory(iter->first, iter->second);
			iter++;
		}
	}
	/*
	_timer.stop();
	cout << __FILE__ << " " << __LINE__ << " " << _timer.duration() << endl;
	_timer.start();
	*/
	return outImage;
}

template <class T> SPIIT ImageTask<T>::_prepareOutputImage(
    const ImageInterface<T>& image, Bool dropDeg
) const {
    if (! _outname.empty()) {
        _removeExistingFileIfNecessary(_outname, _overwrite);
    }
    static const Record empty;
    static const String emptyString;
    auto outImage = SubImageFactory<T>::createImage(
        image, _outname, empty, emptyString, dropDeg,
        _overwrite, True, False, False
    );
    if (! _suppressHistory) {
        ImageHistory<T> history(outImage);
        vector<std::pair<String, String> >::const_iterator end = _newHistory.end();
        vector<std::pair<String, String> >::const_iterator iter = _newHistory.begin();
        while (iter != end) {
            history.addHistory(iter->first, iter->second);
            iter++;
        }
    }
    return outImage;
}

}

