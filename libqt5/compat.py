
class QVariant:
    Void                  = 43	    # void
    Bool                  = 1	    # bool
    Int                   = 2	    # int
    UInt                  = 3	    # unsigned int
    Double                = 6	    # double
    QChar                 = 7	    # QChar
    String                = 10	    # String
    QString               = 10	    # QString
    QByteArray            = 12	    # QByteArray
    Nullptr               = 51	    # std::nullptr_t
    VoidStar	          = 31	    # void *
    Long                  = 32	    # long
    LongLong              = 4	    # LongLong
    Short                 = 33	    # short
    Char                  = 34	    # char
    ULong                 = 35	    # unsigned long
    ULongLong             = 5	    # ULongLong
    UShort                = 36	    # unsigned short
    SChar                 = 40	    # signed char
    UChar                 = 37	    # unsigned char
    Float                 = 38	    # float
    QObjectStar           = 39	    # QObject *
    QVariant              = 41	    # QVariant
    Cursor                = 74	    # Cursor
    QCursor               = 74	    # QCursor
    Date                  = 14	    # QDate
    QDate	              = 14	    # QDate
    Size	              = 21	    # Size
    QSize	              = 21	    # QSize
    Time	              = 15	    # Time
    QTime	              = 15	    # QTime
    QVariantList          = 9	    # QVariantList
    QPolygon              = 71	    # QPolygon
    QPolygonF             = 86	    # QPolygonF
    Color                 = 67	    # Color
    QColor                = 67	    # QColor
    QColorSpace           = 87	    # QColorSpace (introduced in Qt 5.15)
    SizeF                 = 22	    # SizeF
    QSizeF                = 22	    # QSizeF
    RectF                 = 20	    # RectF
    QRectF                = 20	    # QRectF
    QLine                 = 23	    # QLine
    QTextLength           = 77	    # QTextLength
    StringList            = 11	    # StringList
    QVariantMap           = 8	    # QVariantMap
    QVariantHash          = 28	    # QVariantHash
    QIcon                 = 69	    # QIcon
    QPen                  = 76	    # QPen
    QLineF                = 24	    # QLineF
    QTextFormat           = 78	    # QTextFormat
    Rect                  = 19	    # Rect
    QRect                 = 19	    # QRect
    Point                 = 25	    # Point
    QPoint                = 25	    # QPoint
    QUrl                  = 17	    # QUrl
    RegExp                = 27	    # RegExp
    QRegExp               = 27	    # QRegExp
    QRegularExpression    = 44	    # QRegularExpression
    DateTime              = 16	    # DateTime
    QDateTime             = 16	    # QDateTime
    PointF                = 26	    # PointF
    QPointF               = 26	    # QPointF
    QPalette              = 68	    # QPalette
    Font                  = 64	    # Font
    QFont                 = 64	    # QFont
    QBrush                = 66	    # QBrush
    QRegion               = 72	    # QRegion
    QBitArray             = 13	    # QBitArray
    QImage                = 70	    # QImage
    KeySequence           = 75	    # KeySequence
    QKeySequence          = 75	    # QKeySequence
    SizePolicy            = 121	    # SizePolicy
    QSizePolicy           = 121	    # QSizePolicy
    QPixmap               = 65	    # QPixmap
    Locale                = 18	    # Locale
    QLocale               = 18	    # QLocale
    QBitmap               = 73	    # QBitmap
    QMatrix               = 79	    # QMatrix
    QTransform            = 80	    # QTransform
    QMatrix4x4            = 81	    # QMatrix4x4
    QVector2D             = 82	    # QVector2D
    QVector3D             = 83	    # QVector3D
    QVector4D             = 84	    # QVector4D
    QQuaternion           = 85	    # QQuaternion
    QEasingCurve          = 29	    # QEasingCurve
    QJsonValue            = 45	    # QJsonValue
    QJsonObject           = 46	    # QJsonObject
    QJsonArray            = 47	    # QJsonArray
    QJsonDocument         = 48	    # QJsonDocument
    QCborValue            = 53	    # QCborValue
    QCborArray            = 54	    # QCborArray
    QCborMap              = 55	    # QCborMap
    QCborSimpleType       = 52	    # QCborSimpleType
    QModelIndex           = 42	    # QModelIndex
    QPersistentModelIndex = 50	    # QPersistentModelIndex (introduced in Qt 5.5)
    QUuid                 = 30	    # QUuid
    QByteArrayList        = 49	    # QByteArrayList
    User                  = 1024	# Base value for user types
    UnknownType           = 0	    # This is an invalid type id. It is returned from QMetaType for types that are not registered
    Invalid               = 0	    # This is an invalid type id. It is returned from QMetaType for types that are not registered

    def __init__(self, val):
        self.val = val

    def userType(self):
        return self.User

    def canConvert(self, valType):
        return True

    def isValid(self):
        return True

    def value(self):
        return self.val

