from iso8601 import parse_date
from datetime import date

class JSValueConverter:
    """I convert values from and to JavaScript, both sides."""

    def __init__(self, jsName):
        self.jsName = jsName

    def existsIn(self, requestDict):
        if self.jsName in requestDict:
            return True
        return False

    def valueFromJS(self, requestDict):
        value = requestDict.get(self.jsName, None)
        if value is None:
            return None

        return self.convertFromJS(safe_value=value)

    def valueToJS(self, value):
        if value is not None:
            return self.convertToJS(value)
        return None

    def convertFromJS(self, safe_value):
        raise NotImplementedError

    def convertToJS(self, safe_value):
        raise NotImplementedError


class StringValueConverter(JSValueConverter):
    def convertFromJS(self, safe_value):
        return safe_value

    def convertToJS(self, safe_value):
        return str(safe_value)


class DojoComboValueConverter(StringValueConverter):
    def convertFromJS(self, safe_value):
        if not safe_value:
            return None

        if safe_value[-1] == '*':
            return safe_value[:-1]
        return safe_value


class DateTimeValueConverter(JSValueConverter):
    timezone = None
    
    def convertToJS(self, safe_value):
        return safe_value.isoformat()

    def convertFromJS(self, safe_value):
        return parse_date(safe_value, self.timezone)


class DateValueConverter(JSValueConverter):
    def convertToJS(self, safe_value):
        return safe_value.strftime("%Y-%m-%d")

    def convertFromJS(self, safe_value):
        try:
            y, m, d = safe_value.split('-', 2)
        except ValueError:
            return None

        try:
            y = int(y)
            m = int(m)
            d = int(d)
        except (TypeError, ValueError):
            return None

        return date(y, m, d)


class BooleanConverter(JSValueConverter):
    def convertFromJS(self, safe_value):
        if safe_value == 'true':
            return True
        return False

    def convertToJS(self, safe_value):
        if safe_value:
            return 'true'

        if safe_value is None:
            return 'null'

        return 'false'


class IntegerConverter(JSValueConverter):
    def __init__(self, jsName, max=None, min=None):
        JSValueConverter.__init__(self, jsName)
        self.min = min
        self.max = max

    def convertFromJS(self, safe_value):
        try:
            i = int(safe_value)
        except (TypeError, ValueError):
            return None

        if self.min is not None:
            if i < self.min:
                return None

        if self.max is not None:
            if i > self.max:
                return None

        return i

    def convertToJS(self, safe_value):
        return str(safe_value)
