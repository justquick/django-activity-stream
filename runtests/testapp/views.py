from drf_spectacular.views import AUTHENTICATION_CLASSES
from drf_spectacular.settings import spectacular_settings
from drf_spectacular.plumbing import get_relative_url, set_query_parameters
from rest_framework.views import APIView
from rest_framework.reverse import reverse
from rest_framework.response import Response
from rest_framework.renderers import TemplateHTMLRenderer
from drf_spectacular.utils import extend_schema, extend_schema_serializer, \
    OpenApiParameter, OpenApiTypes, OpenApiExample, OpenApiResponse


class SchemaExtender:
    def __init__(self, router):
        self.router = router

    def example(self, name, request_only=True, **value):
        return OpenApiExample(name, request_only=request_only, value=value)

    def ctype(self, prefix=None, help=None, path=True, required=True):
        return {
            'name': f'{prefix}_content_type_id' if prefix else 'content_type_id',
            'description': f'Primay key of the ContentType {help}',
            'required': required,
            'location': OpenApiParameter.PATH if path else OpenApiParameter.QUERY
        }

    def objid(self, prefix=None, help=None, path=True, required=True):
        return {
            'name': f'{prefix}_object_id' if prefix else 'object_id',
            'description': f'Primay key of the instance {help}',
            'required': required,
            'location': OpenApiParameter.PATH if path else OpenApiParameter.QUERY
        }

    def action_model_stream(self):
        return {
            'parameters': [self.ctype(help='to show *all* actions from the specific model')],
            'responses': {
                200: OpenApiResponse(OpenApiTypes.JSON_PTR)
            }
        }

    def action_send(self):
        return {
            'responses': {
                201: OpenApiResponse(None, 'No content if sucessful'),
                400: OpenApiResponse(None, 'Bad user input. Missing verb'),
                404: OpenApiResponse(None, 'target/action_object not found'),
            },
            'examples': [
                self.example(
                    'Join a group',
                    request_only=True,
                    verb='join',
                    target_object_id=1,
                    target_content_type_id=10,
                    public=True
                )
            ]
        }

    def extend_viewset(self, viewset, basename):
        for name, obj in vars(viewset).items():
            if hasattr(obj, 'detail') and hasattr(obj, 'url_name'):
                action_attr = f'{basename}_{name}'
                if hasattr(self, action_attr):
                    schema = getattr(self, action_attr)()
                    params = schema.pop('parameters', None)
                    if params:
                        schema['parameters'] = [OpenApiParameter(**param) for param in params]
                    obj = extend_schema(**schema)(obj)
                    setattr(viewset, name, obj)
            if name == 'serializer_class':
                serializer_attr = f'{basename}_serializer'
                if hasattr(self, serializer_attr):
                    schema = getattr(self, serializer_attr)(obj)
                    obj = extend_schema_serializer(**schema)
                    setattr(viewset, name, obj)
        return viewset

    @property
    def urls(self):
        for prefix, viewset, basename in self.router.registry:
            self.extend_viewset(viewset, basename)
        return self.router.urls


class SpectacularRapiDocView(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    permission_classes = spectacular_settings.SERVE_PERMISSIONS
    authentication_classes = AUTHENTICATION_CLASSES
    url_name = 'schema'
    url = None
    template_name = 'rapidoc.html'
    title = spectacular_settings.TITLE

    @extend_schema(exclude=True)
    def get(self, request, *args, **kwargs):
        schema_url = self.url or get_relative_url(reverse(self.url_name, request=request))
        schema_url = set_query_parameters(schema_url, lang=request.GET.get('lang'))
        return Response(
            data={
                'title': self.title,
                'dist': 'https://cdn.jsdelivr.net/npm/rapidoc@latest',
                'schema_url': schema_url,
            },
            template_name=self.template_name,
        )
