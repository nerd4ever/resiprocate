
#ifndef NERD4EVER_KAYA_SDK_LIB_EXPORT_H
#define NERD4EVER_KAYA_SDK_LIB_EXPORT_H

#ifdef DUM_STATIC_DEFINE
#  define NERD4EVER_KAYA_SDK_LIB_EXPORT
#  define DUM_NO_EXPORT
#else
#  ifndef NERD4EVER_KAYA_SDK_LIB_EXPORT
#    ifdef dum_EXPORTS
        /* We are building this library */
#      define NERD4EVER_KAYA_SDK_LIB_EXPORT 
#    else
        /* We are using this library */
#      define NERD4EVER_KAYA_SDK_LIB_EXPORT 
#    endif
#  endif

#  ifndef DUM_NO_EXPORT
#    define DUM_NO_EXPORT 
#  endif
#endif

#ifndef DUM_DEPRECATED
#  define DUM_DEPRECATED __attribute__ ((__deprecated__))
#endif

#ifndef DUM_DEPRECATED_EXPORT
#  define DUM_DEPRECATED_EXPORT NERD4EVER_KAYA_SDK_LIB_EXPORT DUM_DEPRECATED
#endif

#ifndef DUM_DEPRECATED_NO_EXPORT
#  define DUM_DEPRECATED_NO_EXPORT DUM_NO_EXPORT DUM_DEPRECATED
#endif

#if 0 /* DEFINE_NO_DEPRECATED */
#  ifndef DUM_NO_DEPRECATED
#    define DUM_NO_DEPRECATED
#  endif
#endif

#endif /* NERD4EVER_KAYA_SDK_LIB_EXPORT_H */
