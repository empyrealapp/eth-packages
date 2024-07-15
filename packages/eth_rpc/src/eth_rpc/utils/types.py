AnnotatedTypeNames = {"AnnotatedMeta", "_AnnotatedAlias"}


def is_annotation(t):
    return type(t).__name__ in AnnotatedTypeNames
