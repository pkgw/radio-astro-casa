//# DSScreenText : Implementation of a relative screen pos. DSText
//# Copyright (C) 1998,1999,2000,2001,2002
//# Associated Universities, Inc. Washington DC, USA.
//#
//# This library is free software; you can redistribute it and/or modify it
//# under the terms of the GNU Library General Public License as published by
//# the Free Software Foundation; either version 2 of the License, or (at your
//# option) any later version.
//#
//# This library is distributed in the hope that it will be useful, but WITHOUT
//# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
//# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Library General Public
//# License for more details.
//#
//# You should have received a copy of the GNU Library General Public License
//# along with this library; if not, write to the Free Software Foundation,
//# Inc., 675 Massachusetts Ave, Cambridge, MA 02139, USA.
//#
//# Correspondence concerning AIPS++ should be addressed as follows:
//#        Internet email: aips2-request@nrao.edu.
//#        Postal address: AIPS++ Project Office
//#                        National Radio Astronomy Observatory
//#                        520 Edgemont Road
//#                        Charlottesville, VA 22903-2475 USA
//#
//# $Id:
#ifndef TRIALDISPLAY_DSSCREENTEXT_H
#define TRIALDISPLAY_DSSCREENTEXT_H

#include <casa/aips.h>
#include <casa/Arrays/Vector.h>
#include <casa/Arrays/Matrix.h>

#include <display/DisplayShapes/DSText.h>
#include <display/DisplayShapes/DisplayShapeWithCoords.h>

namespace casacore{

	class Record;
}

namespace casa { //# NAMESPACE CASA - BEGIN

// <summary>
// Implementation of a relative screen pos. DSText
// </summary>

	class PixelCanvas;
	class DSWorldText;
	class DSPixelText;

	class DSScreenText : public DSText , public DisplayShapeWithCoords {

	public:

		DSScreenText();
		DSScreenText(const casacore::Record& settings, PixelCanvas* pc);
		DSScreenText(DSPixelText& other, PixelCanvas* pc);
		DSScreenText(DSWorldText& other);

		virtual ~DSScreenText();

		virtual void recalculateScreenPosition();
		virtual casacore::Bool setOptions(const casacore::Record& settings);
		virtual casacore::Record getOptions();

		// These are so we can monitor if the text is moved and update our
		// relative position
		virtual void move(const casacore::Float& dX, const casacore::Float& dY);
		virtual void setCenter(const casacore::Float& xPos, const casacore::Float& yPos);

		virtual casacore::Record getRawOptions() {
			return DSText::getOptions();
		}
	private:

		PixelCanvas* itsPC;
		casacore::Vector<casacore::Float> itsRelativeCenter;

		virtual casacore::Vector<casacore::Float> relToScreen(const casacore::Vector<casacore::Float>& rel);
		virtual casacore::Vector<casacore::Float> screenToRel(const casacore::Vector<casacore::Float>& screen);
		virtual void updateRC();
	};

} //# NAMESPACE CASA - END

#endif
