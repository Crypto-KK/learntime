from django.contrib import messages
from django.db.models.base import ModelBase
from django import forms
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView


class CurdViewImproperlyConfigure(Exception):
    pass


class CrudViewFactory:
    """增删改查生成工厂"""
    def __init__(self, obj_name, obj_name_plural, model_class, attrs_dict, mixins=()):
        """
        :param obj_name: 单个对象的名称
        :param obj_name_plural: 对象的复数名称
        :param model_class: 对象的模型类
        :param attrs_dict: 类视图的属性
        :param mixins: 类视图的组合类
        """
        self._obj_name = obj_name
        self._obj_name_plural = obj_name_plural
        self._mixins = mixins
        self._attrs = attrs_dict
        self._model_class = model_class

        if not isinstance(self._model_class, ModelBase):
            raise CurdViewImproperlyConfigure("model class必须为django的Model！")

    @staticmethod
    def get_success_url(instance, msg, reverse_url):
        messages.warning(instance.request, msg)
        return reverse_lazy(reverse_url)

    def create_list_view(self):
        """创建列表视图"""
        return type(f'{self._obj_name}ListView', self._mixins + (ListView, ), {
            **self._attrs,
            'template_name': f"{self._obj_name}/list.html",
            'context_object_name': self._obj_name_plural,
            "model": self._model_class
        })

    def create_detail_view(self):
        """创建详情视图"""
        return type(f'{self._obj_name}DetailView', self._mixins + (DetailView, ), {
            **self._attrs,
            'template_name': f"{self._obj_name}/detail.html",
            'context_object_name': self._obj_name,
            "model": self._model_class
        })

    def create_create_view(self, use_all_fields, form_class, success_message, reverse_url):
        """创建添加视图
        :param use_all_fields: 是否使用所有模型字段
        :param form_class: 自定义模型类
        :param success_message: 创建成功的提示
        :param reverse_url: 创建成功后跳转
        """
        class FormKlass(forms.ModelForm):
            class Meta:
                fields = '__all__'
                model = self._model_class

        def get_success_url(instance):
            messages.success(instance.request, success_message)
            return reverse_lazy(reverse_url)

        return type(f'{self._obj_name}CreateView', self._mixins + (CreateView, ), {
            **self._attrs,
            'template_name': f"{self._obj_name}/create.html",
            'context_object_name': self._obj_name_plural,
            "model": self._model_class,
            'form_class': FormKlass if use_all_fields else form_class,
            'get_success_url': get_success_url
        })

    def create_delete_view(self, success_message, reverse_url):
        """创建删除视图"""
        def get_success_url(instance):
            messages.warning(instance.request, success_message)
            return reverse_lazy(reverse_url)

        return type(f'{self._obj_name}DeleteView', self._mixins + (DeleteView, ), {
            **self._attrs,
            'template_name': f"{self._obj_name}/delete.html",
            'context_object_name': self._obj_name,
            "model": self._model_class,
            'get_success_url': get_success_url
        })

    def create_update_view(self, use_all_fields, form_class, success_message, reverse_url):
        """创建更新视图
        :param use_all_fields: 是否使用所有模型字段
        :param form_class: 自定义模型类
        :param success_message: 更新成功的提示
        :param reverse_url: 更新成功后跳转
        """
        def get_success_url(instance):
            messages.success(instance.request, success_message)
            return reverse_lazy(reverse_url)

        class FormKlass(forms.ModelForm):
            class Meta:
                fields = '__all__'
                model = self._model_class

        return type(f'{self._obj_name}UpdateView', self._mixins + (UpdateView, object), {
            **self._attrs,
            'template_name': f"{self._obj_name}/update.html",
            "model": self._model_class,
            'get_success_url': get_success_url,
            'form_class': FormKlass if use_all_fields else form_class,
        })
