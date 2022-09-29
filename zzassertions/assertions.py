import inspect
import logging
import re
from numbers import Real

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


def _format_message(left_operand, operator, right_operand, fist_argument, second_argument):
    msg = ['expected: %s %s %s' % (left_operand, operator, right_operand)]
    if not _is_python_literal(left_operand):
        msg.append('%s: "%s"' % (left_operand, fist_argument))
    if not _is_python_literal(right_operand):
        msg.append('%s: "%s"' % (right_operand, second_argument))
    return '; '.join(msg)


def _is_python_literal(value):  # pylint: disable=too-many-return-statements

    if re.match(r'^[\'\"].+[\"\']$', value):
        return True

    if re.match(r'^-?[0-9xA-Fa-f]+L?$', value):
        return True

    if re.match(r'^-?[0-9]+.[0-9Ee\-\+]+$', value):
        return True

    if re.match(r'^\[.+?\]$', value):
        return True

    if re.match(r'^\(.+?\)$', value):
        return True

    if re.match(r'^{.+?}$', value):
        return True

    return False


def _get_expression_members(expression):
    operands = [r" \| ",
                r" \^ ",
                r" & ",
                r" << ",
                r" >> ",
                r" \+ ",
                r" - ",
                r" // ",
                r" / ",
                r" %% ",
                r" == ",
                r" != ",
                r" <= ",
                r" < ",
                r" >= ",
                r" > ",
                r" \*\* ",
                r" \* ",
                r" is not ",
                r" is ",
                r" or not in ",
                r" not in ",
                r" or in ",
                r" in ",
                r" or ",
                r" and "]

    return [item.strip() for item in re.split(r'|'.join(operands), expression)]


def _get_parameters(stack=None, exp=None):
    if stack is not None:
        expression = stack[1].code_context[0].strip()
    else:
        expression = exp

    if not expression.startswith('assert'):
        raise AttributeError('Multi-line assertion is not supported')
    groups = re.search(r'assert\w+?\('
                       r'(?P<first_param>'
                       r'(?P<first_param_quote>[\"\'])?'
                       r'.+?'
                       r'(?(first_param_quote)[\"\']))'

                       r'(?P<main_comma> ?, ?)?'
                       r'(?(main_comma)'
                       r'(?P<second_param>'
                       r'(?P<second_param_quote>[\"\'])?'
                       r'.+?'
                       r'(?(second_param_quote)[\"\']))'

                       r'(?P<tolerance_comma> ?, ?)?'
                       r'(?(tolerance_comma)'
                       r'(tolerance ?\=)?'
                       r'.+?'
                       r')'
                       r')'
                       r'\)$',
                       expression)

    if not groups:
        raise AttributeError('Not able to parse %s' % expression)
    return groups.group('first_param'), groups.group('second_param')


def _get_local_vars(stack):
    vars_dict = {}

    local_vars = stack[1].frame.f_locals
    for key, value in local_vars.items():

        if key == 'self':
            continue
        vars_dict[key] = value
    return vars_dict


def assertTrue(condition):  # pylint: disable=invalid-name
    stack = inspect.stack()
    left, _ = _get_parameters(stack)
    local_vars = _get_local_vars(stack)
    members = _get_expression_members(left)

    msg = ['expected: %s is True' % left]
    for member in members:
        if member in local_vars:
            msg.append('%s: "%s"' % (member, local_vars[member]))

    if condition:
        LOG.info("; ".join(msg))
    else:
        error_msg = '%s (%s) is not True' % (condition, type(condition))
        raise AssertionError(error_msg)


def assertFalse(condition):  # pylint: disable=invalid-name
    stack = inspect.stack()
    left, _ = _get_parameters(stack)
    local_vars = _get_local_vars(stack)
    members = _get_expression_members(left)

    msg = ['expected: "%s" is False' % left]
    for member in members:
        if member in local_vars:
            msg.append('%s: "%s"' % (member, local_vars[member]))

    if not condition:
        LOG.info("; ".join(msg))
    else:
        error_msg = '%s (%s) is not False' % (condition, type(condition))
        raise AssertionError(error_msg)


def assertEquals(actual, expected, tolerance=0):  # pylint: disable=invalid-name
    stack = inspect.stack()
    left, right = _get_parameters(stack)

    if not isinstance(tolerance, Real) or tolerance < 0:
        raise TypeError("The tolerance has to be a positive real number. Encountered: %s (%s)"
                        % (tolerance, type(tolerance)))

    if tolerance > 0:
        try:
            equals = abs(actual - expected) < tolerance
        except TypeError as exc:
            raise TypeError("Comparison with tolerance is only supported for Numbers. "
                            "Operands actual: %s (%s), expected: %s (%s)"
                            % (actual, type(actual), expected, type(expected))) from exc
    else:
        equals = actual == expected

    if equals:
        if tolerance > 0:
            LOG.info(_format_message(left, 'equals with tolerance %s' % tolerance, right, actual, expected))
        else:
            LOG.info(_format_message(left, 'equals', right, actual, expected))
    else:
        error_msg = '%s (%s) and %s (%s) are not equal' % (actual, type(actual), expected, type(expected))
        if tolerance > 0.0:
            error_msg = error_msg + ' below a tolerance of %s' % tolerance
        raise AssertionError(error_msg)


def assertNotEquals(actual, expected):  # pylint: disable=invalid-name
    stack = inspect.stack()
    left, right = _get_parameters(stack)

    if actual != expected:
        LOG.info(_format_message(left, 'not equals', right, actual, expected))
    else:
        error_msg = '%s (%s) and %s (%s) are equal' % (actual, type(actual), expected, type(expected))
        raise AssertionError(error_msg)


def assertIn(value, iterator):  # pylint: disable=invalid-name
    stack = inspect.stack()
    left, right = _get_parameters(stack)

    if value in iterator:
        LOG.info(_format_message(left, 'in', right, value, iterator))
    else:
        error_msg = ('"%s" not in "%s"' % (value, iterator))
        raise AssertionError(error_msg)


def assertNotIn(value, iterator):  # pylint: disable=invalid-name
    stack = inspect.stack()
    left, right = _get_parameters(stack)

    if value not in iterator:
        LOG.info(_format_message(left, 'not in', right, value, iterator))
    else:
        error_msg = ('"%s" in "%s"' % (value, iterator))
        raise AssertionError(error_msg)
